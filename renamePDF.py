import tkinter as tk
import sys
from PIL import Image, ImageTk
import pymupdf
import os

image = None

def stop_app(rect, dirs):
    # Close tkinter winder
    root.destroy()
    for pdf in dirs:
        doc = pymupdf.open(pdf)
        page = doc[0]
        print(rect)
        # Find selected text in each document
        title = page.get_text("words", rect)[0][4]
        title = title.replace("\n", "")
        doc.close()
        # Rename the file, taking path into account
        if len(title) > 0:
            os.rename(pdf, os.path.dirname(pdf) + '\\' + title + '.pdf')
    input("Press enter to close")

class App:
    def __init__(self, root, files):
        self.root = root
        # Open first doc as reference
        doc = pymupdf.open(files[0])
        page = doc[0]

        #print(page.mediabox_size)

        # Pixmap -> Image -> PhotoImage -> add to canvas
        pix = page.get_pixmap(dpi=72)

        mode = "RGBA" if pix.alpha else "RGB"
        image_ = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        global image
        image = ImageTk.PhotoImage(image_)
        print(image_.size[0], image_.size[1])
        self.canvas = tk.Canvas(root, width=image_.size[0], height=image_.size[1], bg="white")
        self.canvas.create_image(10, 10, anchor=tk.NW, image=image)
        self.canvas.pack()

        self.doc = doc
        self.files = files

        # Initialize start coordinates and the rectangle ID
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None
        self.select = tk.Button(root, command = self.submit_selection, text="Select area")
        self.select.pack()
        self.selected = tk.StringVar()
        self.selected.set("Currently selected:")
        self.selected_label = tk.Label(root, textvariable=self.selected)
        self.selected_label.pack()


        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

    def submit_selection(self):
        self.doc.close()
        stop_app([self.start_x, self.start_y, self.end_x, self.end_y], self.files)

    def start_drag(self, event):
        self.canvas.delete(self.rect_id)
        # Record the starting coordinates
        self.start_x = event.x
        self.start_y = event.y

        # Create a rectangle and store its ID
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="blue", width=2
        )

    def drag(self, event):
        # Update the rectangle's dimensions as the mouse moves
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def stop_drag(self, event):
        # Optionally perform some action after the drag is complete
        print(f"Rectangle created from ({self.start_x}, {self.start_y}) to ({event.x}, {event.y})")
        self.end_x = event.x
        self.end_y = event.y
        text = self.doc[0].get_text("words", [self.start_x, self.start_y, self.end_x, self.end_y])
        if len(text) > 0:
            self.selected.set("Currently selected: " + (text[0][4]))
        else:
            self.selected.set("Currently selected: -")


if __name__ == "__main__":
    # Ignore first arg, since that is the name of the program
    droppedFiles = sys.argv[1:]
    print(droppedFiles)
    root = tk.Tk()
    app = App(root, droppedFiles)
    root.mainloop()