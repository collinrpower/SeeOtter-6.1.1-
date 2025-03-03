import os
import shutil
import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Configure logging
logging.basicConfig(
    filename="backup.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Camera Files")
        self.destination_folders = []
        self.create_widgets()

    def create_widgets(self):
        # Instructions
        instruction_text = (
            "1. Backup Camera Files to hard drive\n"
            "a. Select the folder to backup\n"
            "b. Add one or more destination folders\n"
            "c. Click 'Start Backup' to copy the folder to each destination"
        )
        tk.Label(self.root, text=instruction_text, justify="left").grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Source folder selection
        tk.Label(self.root, text="Source Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.source_folder = tk.StringVar()
        tk.Entry(self.root, textvariable=self.source_folder, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_source_folder).grid(row=1, column=2, padx=10, pady=5)

        # Destination folder selection
        tk.Button(self.root, text="Add Destination Folder", command=self.add_destination_folder).grid(row=2, column=0, columnspan=3, padx=10, pady=5)

        # Frame to display added destination folders
        self.dest_frame = tk.Frame(self.root)
        self.dest_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        # Start Backup button
        tk.Button(self.root, text="Start Backup", command=self.start_backup).grid(row=5, column=2, padx=10, pady=10)

    def browse_source_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)

    def add_destination_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_folders.append(folder)
            tk.Label(self.dest_frame, text=folder).pack(anchor="w")

    def start_backup(self):
        source = self.source_folder.get()
        if not source:
            messagebox.showerror("Error", "Please select a source folder.")
            logging.error("Backup failed: No source folder selected.")
            return
        if not self.destination_folders:
            messagebox.showerror("Error", "Please add at least one destination folder.")
            logging.error("Backup failed: No destination folders selected.")
            return

        self.progress["maximum"] = len(self.destination_folders)
        self.progress["value"] = 0

        # Run backup in a separate thread to allow UI updates
        threading.Thread(target=self.do_backup, args=(source,), daemon=True).start()

    def do_backup(self, source):
        for dest in self.destination_folders:
            backup_path = os.path.join(dest, f"{os.path.basename(source)}_backup")
            try:
                if os.path.exists(backup_path):
                    self.root.after(0, lambda bp=backup_path: messagebox.showwarning("Warning", f"Backup folder already exists: {bp}"))
                    logging.warning(f"Backup skipped: Folder already exists at {backup_path}")
                else:
                    shutil.copytree(source, backup_path)
                    logging.info(f"Backup successful: {backup_path}")
            except Exception as e:
                self.root.after(0, lambda bp=backup_path, err=e: messagebox.showerror("Error", f"Failed to backup to {bp}: {err}"))
                logging.error(f"Backup failed for {backup_path}: {e}")
            # Safely update progress bar on the main thread
            self.root.after(0, self.update_progress)

        self.root.after(0, lambda: messagebox.showinfo("Success", "Backup completed successfully!"))
        logging.info("Backup process completed.")
        self.root.after(0, self.root.quit)

    def update_progress(self):
        self.progress["value"] += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
