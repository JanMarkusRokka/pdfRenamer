import tkinter as tk
import sys
from PIL import Image, ImageTk
import pymupdf
import os

image = None

def stop_app(rect, dirs):
    # Close tkinter winder
    root.destroy()
    i = 1
    dir_count = str(len(dirs))
    for pdf in dirs:
        doc = pymupdf.open(pdf)
        page = doc[0]
        page.set_rotation(0)
        # Find selected text in each document
        title = page.get_text("words", rect)[0][4]
        title = title.replace("\n", "")
        doc.close()
        # Rename the file, taking path into account
        final = pdf
        if len(title) > 0:
            while os.path.exists(os.path.dirname(pdf) + '\\' + title + '.pdf'):
                title+=" +"
            os.rename(pdf, os.path.dirname(pdf) + '\\' + title + '.pdf')
            final = os.path.dirname(pdf) + '\\' + title + '.pdf'
        print(final)
        print(str(i) + "/" + dir_count)
        i+=1
    input("Press enter to close")

class App:
    def __init__(self, root, files):
        self.root = root
        self.zoom = 1
        # Open first doc as reference
        doc = pymupdf.open(files[0])
        self.page = doc[0]
        self.page.set_rotation(0)

        #print(page.mediabox_size)

        # Pixmap -> Image -> PhotoImage -> add to canvas
        pix = self.page.get_pixmap(dpi=round(72 * self.zoom)) # 72

        mode = "RGBA" if pix.alpha else "RGB"
        image_ = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        global image
        image = ImageTk.PhotoImage(image_)
        print(image_.size[0], image_.size[1])

        self.canvas = tk.Canvas(root, width=image_.size[0], height=image_.size[1], bg="white")
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=image)

        self.zoom_in = tk.Button(root, command = self.zoom_in, text = "+")
        self.zoom_out = tk.Button(root, command = self.zoom_out, text = "-")

        self.zoom_in.pack()
        self.zoom_out.pack()
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
        self.draw_text_rects()

    def zoom_in(self):
        self.change_zoom(1.25)
    def zoom_out(self):
        self.change_zoom(0.8)

    def draw_text_rects(self):
        words = self.page.get_text("words")
        for word in words:
            rect = [i * self.zoom for i in word[:4]]
            self.canvas.create_rectangle(
                rect, outline="red", width=2
            )

    def change_zoom(self, zoom_change):
        self.zoom = zoom_change * self.zoom
        self.canvas.delete('all')
        self.selected.set("Currently selected: -")
        pix = self.page.get_pixmap(dpi=round(72 * self.zoom))  # 72
        mode = "RGBA" if pix.alpha else "RGB"
        image_ = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        self.canvas.config(width=image_.size[0], height=image_.size[1])
        global image
        image = ImageTk.PhotoImage(image_)
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.draw_text_rects()

    def submit_selection(self):
        self.doc.close()
        stop_app([i / self.zoom for i in [self.start_x, self.start_y, self.end_x, self.end_y]], self.files)

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
        # Normalize coordinates and ensure same coordinate space
        rect = [i / self.zoom for i in [min(self.start_x, self.end_x), min(self.start_y, self.end_y), max(self.end_x, self.start_x), max(self.end_y, self.start_y)]]

        text = self.doc[0].get_text("words", rect)

        if len(text) > 0:
            self.selected.set("Currently selected: " + (text[0][4]))
        else:
            self.selected.set("Currently selected: -")


if __name__ == "__main__":
    # Ignore first arg, since that is the name of the program
    droppedFiles = sys.argv[1:]
    print("Counted " + str(len(droppedFiles)) + " files")
    root = tk.Tk()
    app = App(root, droppedFiles)
    root.mainloop()