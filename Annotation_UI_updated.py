import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os

class ComicAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Comic Panel Annotator")

        self.image_files = []
        self.current_index = 0
        self.annotations = {}

        self.setup_ui()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="gray")
        self.canvas.grid(row=0, column=0, columnspan=4)

        # Annotation inputs
        self.input_frame = tk.Frame(self.root)
        self.input_frame.grid(row=0, column=4, padx=10, pady=10, sticky="n")

        labels = ["Caption", "Scene Objects", "Characters", "Actions", "Visual Encoders", "Textual Dialogues"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(self.input_frame, text=label + ":").grid(row=i, column=0, sticky="w")
            entry = tk.Entry(self.input_frame, width=40)
            entry.grid(row=i, column=1, pady=5)
            self.entries[label.lower().replace(" ", "_")] = entry

        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.grid(row=1, column=0, columnspan=4, pady=10)

        tk.Button(nav_frame, text="Previous", command=self.prev_image).grid(row=0, column=0, padx=5)
        tk.Button(nav_frame, text="Next", command=self.next_image).grid(row=0, column=1, padx=5)
        tk.Button(nav_frame, text="Save Annotations", command=self.save_annotations).grid(row=0, column=2, padx=5)
        tk.Button(nav_frame, text="Load Images", command=self.load_images).grid(row=0, column=3, padx=5)

    def load_images(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            self.image_files.sort()
            self.current_index = 0
            self.display_image()

    def display_image(self):
        if not self.image_files:
            return

        path = self.image_files[self.current_index]
        img = Image.open(path)

        # Resize based on canvas size
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            cw, ch = 600, 800
        img.thumbnail((cw, ch), Image.LANCZOS)

        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

        panel_id = os.path.basename(path)
        if panel_id in self.annotations:
            data = self.annotations[panel_id]
            self.entries["caption"].delete(0, tk.END)
            self.entries["caption"].insert(0, data.get("caption", ""))
            self.entries["scene_objects"].delete(0, tk.END)
            self.entries["scene_objects"].insert(0, ",".join(data.get("scene", [])))
            self.entries["characters"].delete(0, tk.END)
            self.entries["characters"].insert(0, ",".join(data.get("characters", [])))
            self.entries["actions"].delete(0, tk.END)
            self.entries["actions"].insert(0, ",".join(data.get("actions", [])))
            self.entries["visual_encoders"].delete(0, tk.END)
            self.entries["visual_encoders"].insert(0, ",".join(data.get("visual", {}).get("encoders", [])))
            self.entries["textual_dialogues"].delete(0, tk.END)
            self.entries["textual_dialogues"].insert(0, ";".join(data.get("textual", {}).get("dialogues", [])))
        else:
            for entry in self.entries.values():
                entry.delete(0, tk.END)

    def record_annotation(self):
        if not self.image_files:
            return

        path = self.image_files[self.current_index]
        panel_id = os.path.basename(path)

        annotation = {
            "caption": self.entries["caption"].get(),
            "scene": self.entries["scene_objects"].get().split(","),
            "characters": self.entries["characters"].get().split(","),
            "actions": self.entries["actions"].get().split(","),
            "visual": {
                "panel_image": path,
                "encoders": self.entries["visual_encoders"].get().split(",")
            },
            "textual": {
                "dialogues": self.entries["textual_dialogues"].get().split(";")
            }
        }
        self.annotations[panel_id] = annotation

    def next_image(self):
        self.record_annotation()
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.display_image()

    def prev_image(self):
        self.record_annotation()
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()

    def save_annotations(self):
        self.record_annotation()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"panels": list(self.annotations.values())}, f, indent=4)
            print(f"✅ Saved annotations to {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ComicAnnotator(root)
    root.mainloop()
