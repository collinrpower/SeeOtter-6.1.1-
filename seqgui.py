import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, scrolledtext
import subprocess
import os

def configure_style() -> None:
    style = ttk.Style()
    # Optionally choose a built-in theme: "clam", "alt", "default", "classic"
    style.theme_use("clam")

    # Customize colors/fonts for a more modern look
    style.configure("TFrame", background="#f5f5f5")
    style.configure("TLabel", background="#f5f5f5", font=("Helvetica", 12))
    style.configure("TButton", background="#007BFF", foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=6)
    style.map("TButton", background=[("active", "#0056b3")])
    style.configure("TLabelframe", background="#f5f5f5")
    style.configure("TLabelframe.Label", font=("Helvetica", 12, "bold"), foreground="#333333")


###############################
# SeeOtter Step Definitions
###############################
# Reflects the SeeOtter Workflow Breakdown Document.
# Each step has a title, sub-steps, and a tutorial.

STEPS = [
    {
        "title": "1. Organize and Backup Data",
        "sub_steps": [
            {
                "name": "Backup Camera Files",
                "script": "backup_camera_files.py",
                "tutorial": (
                    "Backup raw images from cameras to multiple locations, "
                    "ensuring no data loss. Use this step to securely copy files "
                    "and verify integrity."
                )
            },
            {
                "name": "Move Image Files (0 and 1 Folders)",
                "script": "move_image_files.py",
                "tutorial": (
                    "Sort images into folders based on camera source (0 vs 1). "
                    "This ensures correct transect assignments and prevents duplicates."
                )
            }
        ]
    },
    {
        "title": "2. Preprocess Images",
        "sub_steps": [
            {
                "name": "Extract Image Metadata",
                "script": "extract_image_metadata.py",
                "tutorial": (
                    "Extract EXIF data such as timestamps and GPS coordinates into a "
                    "CSV file for verification and alignment with transects."
                )
            },
            {
                "name": "Assign Images to Transects",
                "script": "assign_images_to_transects.py",
                "tutorial": (
                    "Use timestamps and GPS data to match images with their respective "
                    "transects. This ensures accurate spatial organization for the survey."
                )
            },
            {
                "name": "Run Preprocessing",
                "script": "run_preprocessing.py",
                "tutorial": (
                    "Crop and align images, apply GPS corrections, and standardize them "
                    "for AI detection. Speeds up and standardizes downstream processing."
                )
            },
            {
                "name": "Classify Images as Land/Water",
                "script": "PercentCoverLand.py",
                "tutorial": (
                    "Classify images by environment (land or water) using a deep learning approach. "
                    "This helps filter out irrelevant images and improve AI detection performance."
                )
            },
        ]
    },
    {
        "title": "3. AI-Assisted Object Detection",
        "sub_steps": [
            {
                "name": "Change Model Weights (Optional)",
                "script": "change_model_weights.py",
                "tutorial": (
                    "Swap YOLO model weights for improved or specialized detection. "
                    "This updates the best.pt file to enhance accuracy."
                )
            },
            {
                "name": "Edit Otter Checker Config (Optional)",
                "script": "edit_otter_checker_config.py",
                "tutorial": (
                    "Adjust the otter_checker_config.json to configure detection categories, "
                    "thresholds, or other model settings."
                )
            },
            {
                "name": "Run SeeOtter Processing",
                "script": "run_seeotter_processing.py",
                "tutorial": (
                    "Process the preprocessed images with the AI model to generate "
                    "preliminary wildlife detections."
                )
            },
        ]
    },
    {
        "title": "4. Final Processing",
        "sub_steps": [
            {
                "name": "Final Processing",
                "script": "final_processing.py",
                "tutorial": (
                    "Clean and organize the validated data to produce final CSV files, "
                    "shapefiles, or reports for ecological analysis."
                )
            }
        ]
    }
]


def run_script(script: str, log_callback) -> None:
    """Execute the specified Python script and log its output.

    Args:
        script (str): Path to the Python script (relative or absolute).
        log_callback (callable): Function to handle logging.
    """
    if not script:
        messagebox.showinfo("Info", "This step requires manual or external intervention.")
        log_callback("[INFO] No script is configured for this step.")
        return
    if not os.path.exists(script):
        messagebox.showerror("Error", f"Script not found: {script}")
        log_callback(f"[ERROR] Script not found: {script}")
        return
    try:
        log_callback(f"[INFO] Running: {os.path.basename(script)}")
        result = subprocess.run(["python", script], capture_output=True, text=True, check=False)
        if result.stdout:
            log_callback(result.stdout.strip())
        if result.stderr:
            log_callback(f"[ERROR] {result.stderr.strip()}")
    except Exception as e:
        log_callback(f"[EXCEPTION] Failed to run {script}: {str(e)}")


class SeeOtterGUI:
    """A Tkinter-based GUI for sequentially running SeeOtter scripts, with a modern look."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI with a modern theme, step-based buttons, tutorials, and a log window.

        Args:
            root (tk.Tk): The main Tkinter window.
        """
        self.root = root
        self.root.title("SeeOtter Sequential Processing GUI")
        self.root.geometry("900x650")

        # Configure the style
        configure_style()

        # Main frame using ttk
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_label = ttk.Label(main_frame, text="SeeOtter Workflow", font=("Helvetica", 18, "bold"))
        header_label.pack(pady=10)

        # Create a scrollable text widget for logs, using ttk for a more modern look
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=100, state="normal")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Steps container
        steps_frame = ttk.Frame(main_frame)
        steps_frame.pack(fill=tk.X, pady=10)

        # Create frames for each step
        for step in STEPS:
            step_frame = ttk.Labelframe(steps_frame, text=step["title"])
            step_frame.pack(fill=tk.X, padx=5, pady=5)

            for sub in step["sub_steps"]:
                subframe = ttk.Frame(step_frame)
                subframe.pack(fill=tk.X, pady=2)

                # Button to run the script
                run_btn = ttk.Button(
                    subframe,
                    text=sub["name"],
                    command=lambda s=sub["script"]: run_script(s, self.log)
                )
                run_btn.pack(side=tk.LEFT, padx=5)

                # Button to show tutorial
                tutorial_btn = ttk.Button(
                    subframe,
                    text="?",
                    command=lambda t=sub["tutorial"]: self.show_tutorial(t)
                )
                tutorial_btn.pack(side=tk.LEFT)

        # Quit button at the bottom
        quit_btn = ttk.Button(main_frame, text="Exit", command=self.root.quit)
        quit_btn.pack(pady=10)

    def show_tutorial(self, tutorial_text: str) -> None:
        """Show a popup with the tutorial text.

        Args:
            tutorial_text (str): The text to display in the tutorial popup.
        """
        messagebox.showinfo("Tutorial", tutorial_text)

    def log(self, message: str) -> None:
        """Append a log message to the log_text widget and auto-scroll.

        Args:
            message (str): The message to log.
        """
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="normal")


def main() -> None:
    """Main entry point for the SeeOtter application."""
    root = tk.Tk()
    app = SeeOtterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()