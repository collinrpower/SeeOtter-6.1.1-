# run_seeotter_processing.py
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

class RunSeeOtterProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Run SeeOtter Processing")
        self.created_folder_path = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        instruction_text = (
            "8. Run SeeOtter Processing\n"
            "a. Create a new survey in SeeOtter\n"
            "b. Point to the newly generated ‘cropped_images_on_tx’ folder\n"
            "c. Start processing the survey\n"
            "d. Validate predictions in OtterChecker9000"
        )
        tk.Label(self.root, text=instruction_text, justify="left").grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        tk.Label(self.root, text="Images Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.created_folder_path, width=50).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        tk.Button(self.root, text="Browse", command=self.browse_created_folder).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(self.root, text="Start SeeOtter", command=self.start_seeotter).grid(row=2, column=1, padx=10, pady=10)

    def browse_created_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.created_folder_path.set(folder)

    def run_script(self, script_path, *args):
        try:
            subprocess.run(['python', script_path, *args], check=True)
            messagebox.showinfo("Success", f"{os.path.basename(script_path)} completed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to run {os.path.basename(script_path)}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def start_seeotter(self):
        images_folder = self.created_folder_path.get()
        if not images_folder:
            messagebox.showerror("Error", "Please select the images folder.")
            return
        script_path = r"start_see_otter_no_survey.py"
        self.run_script(script_path, images_folder)

if __name__ == "__main__":
    root = tk.Tk()
    app = RunSeeOtterProcessingApp(root)
    root.mainloop()
