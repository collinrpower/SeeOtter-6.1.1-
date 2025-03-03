# change_model_weights.py
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class ChangeModelWeightsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Change Model Weights")
        self.create_widgets()

    def create_widgets(self):
        instruction_text = (
            "6. Change Model Weights\n"
            "a. Select new model weights file (.pt)\n"
            "b. Replace the best.pt file in the ModelWeights folder\n"
            "c. Save a backup of the old best.pt file with a timestamp"
        )
        tk.Label(self.root, text=instruction_text, justify="left").grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        tk.Button(self.root, text="Change Model Weights", command=self.change_model_weights_script).grid(row=1, column=1, padx=10, pady=10)

    def change_model_weights_script(self):
        new_weights = filedialog.askopenfilename(title="Select new model weights", filetypes=(("PyTorch model files", "*.pt"), ("All files", "*.*")))
        if new_weights:
            model_weights_folder = os.path.join('SeeOtter_pre_post-main', 'ModelWeights')
            best_weights = os.path.join(model_weights_folder, 'best.pt')
            if os.path.exists(best_weights):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_weights = os.path.join(model_weights_folder, f"best_{timestamp}.pt")
                shutil.copy2(best_weights, backup_weights)
                messagebox.showinfo("Backup", f"Backup of current best.pt created: {backup_weights}")
            shutil.copy2(new_weights, best_weights)
            messagebox.showinfo("Success", "Model weights updated successfully!")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChangeModelWeightsApp(root)
    root.mainloop()
