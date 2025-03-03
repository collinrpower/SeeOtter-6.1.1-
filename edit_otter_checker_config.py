import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import ast
import json


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        vscrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscrollbar.set)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.pack(side="right", fill="y")


class EditOtterCheckerConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Edit Otter Checker Config")

        # Allow row/column expansion
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.load_config()
        self.create_widgets()

    def create_widgets(self):
        instruction_text = (
            "7. Edit Otter Checker Config\n"
            "Modify the image tags and annotation categories.\n"
            "Save changes when done."
        )
        tk.Label(self.root, text=instruction_text, justify="left").grid(
            row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w"
        )

        self.scrollable_frame = ScrollableFrame(self.root)
        self.scrollable_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Image Tags Section
        tk.Label(
            self.scrollable_frame.scrollable_frame, text="Image Tags:"
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.image_tags_entries = []
        for i, tag in enumerate(self.config['IMAGE_TAGS']):
            entry = tk.Entry(self.scrollable_frame.scrollable_frame)
            entry.grid(row=1 + i, column=0, padx=10, pady=2, sticky="w")
            entry.insert(0, tag)
            self.image_tags_entries.append(entry)

        # Annotation Categories Section
        tk.Label(
            self.scrollable_frame.scrollable_frame, text="Annotation Categories:"
        ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.category_rows = []

        # Create 'Add Category' button first
        self.add_button = tk.Button(
            self.scrollable_frame.scrollable_frame,
            text="Add Category",
            command=lambda: self.add_category("", "")
        )
        # Place it a little down (for now at row=1)
        self.add_button.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Load existing categories under the button
        for category, idx in self.config['ANNOTATION_CATEGORIES']:
            self.add_category(category, idx)

        # Save Button
        self.save_button = tk.Button(self.root, text="Save Config", command=self.save_config)
        self.save_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")

    def add_category(self, category, idx):
        # Place the new row where the 'Add Category' button currently is
        current_btn_row = int(self.add_button.grid_info()['row'])
        entry_category = tk.Entry(self.scrollable_frame.scrollable_frame)
        entry_category.insert(0, category)
        entry_category.grid(row=current_btn_row, column=1, padx=10, pady=2, sticky="w")

        entry_index = tk.Entry(self.scrollable_frame.scrollable_frame)
        entry_index.insert(0, idx)
        entry_index.grid(row=current_btn_row, column=2, padx=10, pady=2, sticky="w")

        remove_button = tk.Button(
            self.scrollable_frame.scrollable_frame,
            text="Remove",
            command=lambda: self.remove_category(current_btn_row)
        )
        remove_button.grid(row=current_btn_row, column=3, padx=10, pady=2, sticky="w")

        # Track this row
        self.category_rows.append((current_btn_row, entry_category, entry_index, remove_button))

        # Move the "Add Category" button down 1 row
        self.add_button.grid(row=current_btn_row + 1, column=1, padx=10, pady=10, sticky="w")

    def remove_category(self, row_index):
        row_to_remove = None
        for row_data in self.category_rows:
            if row_data[0] == row_index:
                row_to_remove = row_data
                break

        if not row_to_remove:
            return

        _, entry_cat, entry_idx, btn = row_to_remove
        entry_cat.destroy()
        entry_idx.destroy()
        btn.destroy()
        self.category_rows.remove(row_to_remove)

    def load_config(self):
        config_path = r"Config/otter_checker_config.py"
        self.config = {}
        with open(config_path, 'r') as f:
            content = f.read()

        image_tags_start = content.find("self.IMAGE_TAGS = [")
        image_tags_end = content.find("]", image_tags_start) + 1
        image_tags_data = content[image_tags_start:image_tags_end].split(" = ")[1]
        self.config['IMAGE_TAGS'] = ast.literal_eval(image_tags_data)

        annotation_categories_start = content.find("self.ANNOTATION_CATEGORIES = [")
        annotation_categories_end = content.find("]", annotation_categories_start) + 1
        annotation_categories_data = content[annotation_categories_start:annotation_categories_end].split(" = ")[1]
        self.config['ANNOTATION_CATEGORIES'] = ast.literal_eval(annotation_categories_data)

    def save_config(self):
        # Collect image tags
        new_image_tags = [entry.get() for entry in self.image_tags_entries]

        # Collect annotation categories
        new_annotation_categories = []
        for (_, entry_cat, entry_idx, _) in self.category_rows:
            category = entry_cat.get()
            try:
                index = int(entry_idx.get())
            except ValueError:
                messagebox.showerror("Error", "Annotation category index must be an integer.")
                return
            new_annotation_categories.append((category, index))

        config_path = r"Config/otter_checker_config.py"
        json_config_path = r"otter_checker_config.json"
        backup_path = config_path + ".bak"
        shutil.copy2(config_path, backup_path)

        with open(config_path, 'r') as f:
            content = f.read()

        # Update IMAGE_TAGS
        image_tags_start = content.find("self.IMAGE_TAGS = [")
        image_tags_end = content.find("]", image_tags_start) + 1
        before_image_tags = content[:image_tags_start]
        after_image_tags = content[image_tags_end:]
        updated_image_tags = f"self.IMAGE_TAGS = {new_image_tags}\n"
        content = before_image_tags + updated_image_tags + after_image_tags

        # Update ANNOTATION_CATEGORIES
        annotation_categories_start = content.find("self.ANNOTATION_CATEGORIES = [")
        annotation_categories_end = content.find("]", annotation_categories_start) + 1
        before_annotation_categories = content[:annotation_categories_start]
        after_annotation_categories = content[annotation_categories_end:]
        updated_annotation_categories = f"self.ANNOTATION_CATEGORIES = {new_annotation_categories}\n"
        content = before_annotation_categories + updated_annotation_categories + after_annotation_categories

        with open(config_path, 'w') as f:
            f.write(content)

        if os.path.exists(json_config_path):
            os.remove(json_config_path)

        messagebox.showinfo("Success", f"Configuration updated successfully! Backup saved at {backup_path}")
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = EditOtterCheckerConfigApp(root)
    root.mainloop()
