import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox


class MoveImageFilesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Move Image Files into '0' and '1' Folders")
        self.camera_type = tk.StringVar(value="waldo")
        self.base_folder = tk.StringVar()
        self.source_folder = tk.StringVar()
        self.location_entry_val = tk.StringVar()
        self.camera_entry_val = tk.StringVar()  # Default camera input for generic mode
        self.year_entry_val = tk.StringVar()
        self.mm_dd_entry_val = tk.StringVar()
        self.num_cameras = tk.StringVar(value="1")
        # For generic mode: each entry is a tuple (folder, camera_choice_var, frame)
        self.source_folders = []
        self.create_widgets()

    def create_widgets(self):
        instruction_text = (
            "2. Move image files into ‘0’ and ‘1’ camera folders based on camera type\n"
            "Select the camera type and provide necessary folder details."
        )
        tk.Label(self.root, text=instruction_text, justify="left").grid(row=0, column=0, columnspan=5, padx=10, pady=10)

        tk.Label(self.root, text="Select Camera Type:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Radiobutton(self.root, text="Waldo Camera", variable=self.camera_type, value="waldo",
                       command=self.update_camera_type).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        tk.Radiobutton(self.root, text="Generic Camera", variable=self.camera_type, value="generic",
                       command=self.update_camera_type).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.update_camera_type()

    def update_camera_type(self):
        # Clear widgets from rows 2 and onward.
        for widget in self.root.grid_slaves():
            if int(widget.grid_info().get("row", 0)) >= 2:
                widget.grid_forget()
        if self.camera_type.get() == "waldo":
            self.setup_waldo_widgets()
        else:
            self.setup_generic_widgets()

    def setup_generic_widgets(self):
        # Row 2: Base Folder
        tk.Label(self.root, text="Base Folder:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.base_folder, width=50).grid(row=2, column=1, columnspan=2, padx=10,
                                                                          pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_base_folder).grid(row=2, column=3, padx=10, pady=5)

        # Row 3: Location and Camera input
        tk.Label(self.root, text="Location:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.location_entry_val, width=30).grid(row=3, column=1, padx=10, pady=5,
                                                                                 sticky="w")
        tk.Label(self.root, text="Camera:").grid(row=3, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.camera_entry_val, width=30).grid(row=3, column=3, padx=10, pady=5,
                                                                               sticky="w")

        # Row 4: Year and MM_DD
        tk.Label(self.root, text="Year:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.year_entry_val, width=30).grid(row=4, column=1, padx=10, pady=5,
                                                                             sticky="w")
        tk.Label(self.root, text="MM_DD:").grid(row=4, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.mm_dd_entry_val, width=30).grid(row=4, column=3, padx=10, pady=5,
                                                                              sticky="w")

        # Row 5: Number of Cameras
        tk.Label(self.root, text="Number of Cameras:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.num_cameras, width=10).grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Row 6: Add Source Folder button
        tk.Button(self.root, text="Add Source Folder", command=self.add_source_folder).grid(row=6, column=0, padx=10,
                                                                                            pady=5)

        # Row 7: Scrollable frame for source folders
        self.source_folders_canvas = tk.Canvas(self.root, height=150)
        self.source_folders_canvas.grid(row=7, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.source_folders_canvas.yview)
        self.scrollbar.grid(row=7, column=4, sticky="ns")
        self.source_folders_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.source_folders_frame = tk.Frame(self.source_folders_canvas)
        self.source_folders_canvas.create_window((0, 0), window=self.source_folders_frame, anchor="nw")
        self.source_folders_frame.bind("<Configure>",
                                       lambda e: self.source_folders_canvas.configure(
                                           scrollregion=self.source_folders_canvas.bbox("all")))

        # Row 8: Move Generic Images button
        tk.Button(self.root, text="Move Generic Images", command=self.move_generic_images).grid(row=8, column=1,
                                                                                                padx=10, pady=10)

    def setup_waldo_widgets(self):
        tk.Label(self.root, text="Base Folder:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.base_folder, width=50).grid(row=2, column=1, columnspan=2, padx=10,
                                                                          pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_base_folder).grid(row=2, column=3, padx=10, pady=5)
        tk.Label(self.root, text="Location:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.location_entry_val, width=30).grid(row=3, column=1, padx=10, pady=5,
                                                                                 sticky="w")
        tk.Label(self.root, text="Camera:").grid(row=3, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.camera_entry_val, width=30).grid(row=3, column=3, padx=10, pady=5,
                                                                               sticky="w")
        tk.Label(self.root, text="Year:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.year_entry_val, width=30).grid(row=4, column=1, padx=10, pady=5,
                                                                             sticky="w")
        tk.Label(self.root, text="MM_DD:").grid(row=4, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.mm_dd_entry_val, width=30).grid(row=4, column=3, padx=10, pady=5,
                                                                              sticky="w")
        tk.Label(self.root, text="Source Folder:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.source_folder, width=50).grid(row=5, column=1, columnspan=2, padx=10,
                                                                            pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_source_folder).grid(row=5, column=3, padx=10, pady=5)
        tk.Button(self.root, text="Move Waldo Images", command=self.move_waldo_images).grid(row=6, column=1, padx=10,
                                                                                            pady=10)

    def browse_base_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.base_folder.set(folder)

    def browse_source_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)

    def add_source_folder(self):
        folder = filedialog.askdirectory(title="Select Source Folder for a Camera")
        if folder:
            try:
                n = int(self.num_cameras.get())
            except ValueError:
                messagebox.showerror("Error", "Number of Cameras must be an integer.")
                return
            options = [str(i) for i in range(0, n)]
            default_camera = self.camera_entry_val.get().strip()
            default_val = default_camera if default_camera in options else options[0]
            cam_choice = tk.StringVar(value=default_val)
            frame = tk.Frame(self.source_folders_frame)
            frame.pack(fill="x", padx=5, pady=2)
            tk.Label(frame, text=folder, anchor="w").pack(side="left", fill="x", expand=True)
            tk.OptionMenu(frame, cam_choice, *options).pack(side="left")
            tk.Button(frame, text="Remove", command=lambda: self.remove_source_folder(frame, folder, cam_choice)).pack(
                side="right")
            self.source_folders.append((folder, cam_choice, frame))

    def remove_source_folder(self, frame, folder, cam_choice):
        self.source_folders = [entry for entry in self.source_folders if entry[0] != folder or entry[1] != cam_choice]
        frame.destroy()

    def move_generic_images(self):
        if not self.source_folders:
            messagebox.showerror("Error", "No source folders selected.")
            return
        base_folder = self.base_folder.get().strip()
        location = self.location_entry_val.get().strip()
        camera = self.camera_entry_val.get().strip()
        year = self.year_entry_val.get().strip()
        mm_dd = self.mm_dd_entry_val.get().strip()
        try:
            int(self.num_cameras.get())
        except ValueError:
            messagebox.showerror("Error", "Number of Cameras must be an integer.")
            return
        if not (base_folder and location and year and mm_dd):
            messagebox.showerror("Error", "Please fill out all fields and select all folders.")
            return
        errors = []
        for folder, cam_choice_var, _ in self.source_folders:
            chosen_camera = cam_choice_var.get().strip()
            destination_folder = os.path.join(base_folder,location, camera, year, mm_dd, chosen_camera)
            os.makedirs(destination_folder, exist_ok=True)
            try:
                for item in os.listdir(folder):
                    source_path = os.path.join(folder, item)
                    dest_path = os.path.join(destination_folder, item)
                    shutil.move(source_path, dest_path)
            except Exception as e:
                errors.append(f"Error moving from {folder}: {e}")
        if errors:
            messagebox.showerror("Error", "\n".join(errors))
        else:
            messagebox.showinfo("Success", "Images moved successfully!")

    def move_waldo_images(self):
        source_folder = self.source_folder.get().strip()
        base_folder = self.base_folder.get().strip()
        location = self.location_entry_val.get().strip()
        camera = self.camera_entry_val.get().strip()
        year = self.year_entry_val.get().strip()
        mm_dd = self.mm_dd_entry_val.get().strip()
        if not (source_folder and base_folder and location and camera and year and mm_dd):
            messagebox.showerror("Error", "Please fill out all fields and select all folders.")
            return
        destination_folder = os.path.join(base_folder, location, camera,  year, mm_dd)
        os.makedirs(destination_folder, exist_ok=True)
        try:
            for item in os.listdir(source_folder):
                source_path = os.path.join(source_folder, item)
                if os.path.isfile(source_path):
                    first_char = item[0]
                    if first_char in ['0', '1']:
                        dest_subfolder = os.path.join(destination_folder, first_char)
                        os.makedirs(dest_subfolder, exist_ok=True)
                        dest_path = os.path.join(dest_subfolder, item)
                        shutil.move(source_path, dest_path)
            messagebox.showinfo("Success", f"Images moved successfully to {destination_folder}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move images: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MoveImageFilesApp(root)
    root.mainloop()
