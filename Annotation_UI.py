import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import json
import os

class ComicAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Comic Panel Annotator")

        # File data
        self.image_files = []
        self.current_index = 0
        self.annotations = {}

        # UI Elements
        self.setup_ui()

    def setup_ui(self):
        # Left panel: Image display
        self.image_label = tk.Label(self.root, text="Image will be displayed here.", bg="gray", width=50, height=25)
        self.image_label.grid(row=0, column=0, padx=10, pady=10)

        # Right panel: Annotation input
        self.input_frame = tk.Frame(self.root)
        self.input_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.add_input_fields()
        
        # Navigation and save buttons
        self.navigation_frame = tk.Frame(self.root)
        self.navigation_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.prev_button = tk.Button(self.navigation_frame, text="Previous", command=self.prev_image)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.next_button = tk.Button(self.navigation_frame, text="Next", command=self.next_image)
        self.next_button.grid(row=0, column=1, padx=5)

        self.save_button = tk.Button(self.navigation_frame, text="Save Annotations", command=self.save_annotations)
        self.save_button.grid(row=0, column=2, padx=5)

        # Load images button
        self.load_button = tk.Button(self.root, text="Load Images", command=self.load_images)
        self.load_button.grid(row=2, column=0, columnspan=2, pady=10)

    def add_input_fields(self):
        # Caption
        tk.Label(self.input_frame, text="Caption:").grid(row=0, column=0, sticky="w")
        self.caption_entry = tk.Entry(self.input_frame, width=50)
        self.caption_entry.grid(row=0, column=1, pady=5)

        # Scene objects
        tk.Label(self.input_frame, text="Scene Objects:").grid(row=1, column=0, sticky="w")
        self.scene_entry = tk.Entry(self.input_frame, width=50)
        self.scene_entry.grid(row=1, column=1, pady=5)

        # Characters
        tk.Label(self.input_frame, text="Characters:").grid(row=2, column=0, sticky="w")
        self.character_entry = tk.Entry(self.input_frame, width=50)
        self.character_entry.grid(row=2, column=1, pady=5)

        # Actions
        tk.Label(self.input_frame, text="Actions:").grid(row=3, column=0, sticky="w")
        self.action_entry = tk.Entry(self.input_frame, width=50)
        self.action_entry.grid(row=3, column=1, pady=5)

        # Visual encoders
        tk.Label(self.input_frame, text="Visual Encoders:").grid(row=4, column=0, sticky="w")
        self.visual_entry = tk.Entry(self.input_frame, width=50)
        self.visual_entry.grid(row=4, column=1, pady=5)

        # Textual dialogues
        tk.Label(self.input_frame, text="Textual Dialogues:").grid(row=5, column=0, sticky="w")
        self.textual_entry = tk.Entry(self.input_frame, width=50)
        self.textual_entry.grid(row=5, column=1, pady=5)

    def load_images(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            self.current_index = 0
            self.display_image()

    def display_image(self):
        if self.image_files:
            image_path = self.image_files[self.current_index]
            img = Image.open(image_path)
            img.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="", bg="white")
            self.image_label.image = photo

            # Load previous annotation if it exists
            panel_id = os.path.basename(image_path)
            if panel_id in self.annotations:
                annotation = self.annotations[panel_id]
                self.caption_entry.delete(0, tk.END)
                self.caption_entry.insert(0, annotation.get("caption", ""))
                self.scene_entry.delete(0, tk.END)
                self.scene_entry.insert(0, ",".join(annotation.get("scene", [])))
                self.character_entry.delete(0, tk.END)
                self.character_entry.insert(0, ",".join(annotation.get("characters", [])))
                self.action_entry.delete(0, tk.END)
                self.action_entry.insert(0, ",".join(annotation.get("actions", [])))
                self.visual_entry.delete(0, tk.END)
                self.visual_entry.insert(0, ",".join(annotation.get("visual", {}).get("encoders", [])))
                self.textual_entry.delete(0, tk.END)
                self.textual_entry.insert(0, ",".join(annotation.get("textual", {}).get("dialogues", [])))
            else:
                # Clear the fields if no previous annotation exists
                self.clear_inputs()

    def clear_inputs(self):
        self.caption_entry.delete(0, tk.END)
        self.scene_entry.delete(0, tk.END)
        self.character_entry.delete(0, tk.END)
        self.action_entry.delete(0, tk.END)
        self.visual_entry.delete(0, tk.END)
        self.textual_entry.delete(0, tk.END)

    def record_annotation(self):
        if self.image_files:
            image_path = self.image_files[self.current_index]
            panel_id = os.path.basename(image_path)
            annotation = {
                "caption": self.caption_entry.get(),
                "scene": self.scene_entry.get().split(","),
                "characters": self.character_entry.get().split(","),
                "actions": self.action_entry.get().split(","),
                "visual": {
                    "panel_image": image_path,
                    "encoders": self.visual_entry.get().split(",")
                },
                "textual": {
                    "dialogues": self.textual_entry.get().split(";")
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
        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if save_path:
            with open(save_path, "w") as f:
                json.dump({"panels": list(self.annotations.values())}, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComicAnnotator(root)
    root.mainloop()
