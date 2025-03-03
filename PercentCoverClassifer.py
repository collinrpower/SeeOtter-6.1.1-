import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np
import os
import csv
from datetime import datetime
import threading

def load_model_dialog():
    model_path = filedialog.askopenfilename(
        title="Select a Keras Model File",
        filetypes=[("Keras model files", "*.keras *.h5 *.savedmodel"), ("All files", "*.*")]
    )
    if not model_path:
        raise ValueError("No model file selected.")
    loaded_model = tf.keras.models.load_model(model_path, compile=False)
    loaded_model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss='categorical_crossentropy',  # or 'binary_crossentropy' if binary
        metrics=['accuracy']
    )
    return loaded_model

def preprocess_image(image_path, target_size=(128, 128)):
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize(target_size)
        img_array = np.array(img) / 255.0
        return img_array
    except Exception as e:
        print(f"Failed to preprocess the image {os.path.basename(image_path)}: {e}")
        return None

class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("Generic Image Classifier")
        self.master.geometry("600x300")
        self.master.resizable(False, False)

        self.frame = tk.Frame(self.master, padx=20, pady=20)
        self.frame.pack(expand=True, fill='both')

        self.instruction_label = tk.Label(
            self.frame,
            text="Upload a folder of images for classification.",
            font=("Helvetica", 14)
        )
        self.instruction_label.pack(pady=10)

        self.upload_button = tk.Button(
            self.frame,
            text="Upload Folder & Choose Model",
            command=self.upload_and_predict_folder,
            bg="blue",
            fg="white",
            font=("Helvetica", 12),
            width=25,
            height=2
        )
        self.upload_button.pack(pady=10)

        self.progress_bar = ttk.Progressbar(
            self.frame,
            orient='horizontal',
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)

        self.progress_label = tk.Label(
            self.frame,
            text="",
            font=("Helvetica", 12)
        )
        self.progress_label.pack(pady=5)

        self.folder_path = ""
        self.model = None
        self.classifier_name = ""
        self.not_classifier_name = ""

    def upload_and_predict_folder(self):
        try:
            self.model = load_model_dialog()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model.\n{e}")
            return

        self.classifier_name = simpledialog.askstring(
            "Classifier Name",
            "Enter the name of what you're classifying (e.g., 'Land'):"
        )
        if not self.classifier_name:
            self.classifier_name = "Default"
        self.not_classifier_name = f"Not{self.classifier_name}"

        self.folder_path = filedialog.askdirectory(title="Select Folder Containing Images (use the cropped_images_on_tx/Images folder)")
        if self.folder_path:
            supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
            image_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(supported_extensions)]
            if not image_files:
                messagebox.showinfo("No Images", "No supported image files found.")
                return

            default_csv_name = f"classifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_path = os.path.join(os.path.dirname(self.folder_path), default_csv_name)

            self.upload_button.config(state='disabled')
            self.progress_bar['maximum'] = len(image_files)
            self.progress_bar['value'] = 0
            self.progress_label.config(text="Starting processing...")

            thread = threading.Thread(
                target=self.process_images,
                args=(self.folder_path, image_files, csv_path)
            )
            thread.start()

    def process_images(self, folder_path, image_files, csv_path, batch_size=32):
        self.results = []
        total = len(image_files)
        class_names = [self.classifier_name, self.not_classifier_name]

        try:
            preprocessed_images = []
            valid_filenames = []
            for idx, filename in enumerate(image_files, start=1):
                file_path = os.path.join(folder_path, filename)
                img_array = preprocess_image(file_path)
                if img_array is not None:
                    preprocessed_images.append(img_array)
                    valid_filenames.append(filename)
                else:
                    self.results.append({
                        'Filename': filename,
                        'Classification': 'Error',
                        'Confidence': 'N/A',
                        f'Percent {self.classifier_name} Cover': 'N/A'
                    })
                self.progress_label.config(text=f"Preprocessing {idx}/{total}...")
                self.progress_bar['value'] = idx
                self.master.update_idletasks()

            if preprocessed_images:
                preprocessed_images = np.array(preprocessed_images)
                num_batches = int(np.ceil(len(preprocessed_images) / batch_size))
                for batch_idx in range(num_batches):
                    start = batch_idx * batch_size
                    end = start + batch_size
                    batch_images = preprocessed_images[start:end]
                    batch_filenames = valid_filenames[start:end]

                    predictions = self.model.predict(batch_images)

                    for filename, prediction in zip(batch_filenames, predictions):
                        if prediction.ndim == 0 or (prediction.ndim == 1 and prediction.shape[0] == 1):
                            pred_val = prediction if np.isscalar(prediction) else prediction.item()
                            predicted_label = int(pred_val > 0.5)
                            predicted_class = class_names[predicted_label]
                            confidence = float(pred_val) if predicted_label == 1 else 1.0 - float(pred_val)
                        else:
                            predicted_label = np.argmax(prediction)
                            predicted_class = class_names[predicted_label]
                            confidence = float(prediction[predicted_label])

                        self.results.append({
                            'Filename': filename,
                            'Classification': predicted_class,
                            'Confidence': f"{confidence * 100:.2f}%",
                            f'Percent {self.classifier_name} Cover': 'N/A'
                        })
                    processed = min(end, len(preprocessed_images))
                    self.progress_label.config(text=f"Classifying {processed}/{total}...")
                    self.progress_bar['value'] = processed
                    self.master.update_idletasks()

            self.progress_label.config(text="Processing complete. Launching validation...")
            self.master.update_idletasks()
            # Schedule the ValidationWindow creation in the main thread:
            self.master.after(0, lambda: ValidationWindow(self.master, self.results, csv_path, self.folder_path,
                                                          self.classifier_name, self.not_classifier_name))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred.\n{e}")
        finally:
            self.upload_button.config(state='normal')
            self.progress_label.config(text="Processing complete.")
            self.progress_bar['value'] = 0


class ValidationWindow:
    def __init__(self, master, results, csv_path, folder_path, classifier_name, not_classifier_name):
        self.master = master
        self.results = results
        self.csv_path = csv_path
        self.folder_path = folder_path
        self.classifier_name = classifier_name
        self.not_classifier_name = not_classifier_name

        self.not_classifier_images = [
            img for img in self.results
            if img['Classification'] == self.not_classifier_name
        ]
        self.not_classifier_images.sort(
            key=lambda x: float(x['Confidence'].replace('%','')) if x['Confidence'] != 'N/A' else 0
        )

        self.classifier_images = [
            img for img in self.results
            if img['Classification'] == self.classifier_name
        ]

        self.misclassified_not_classifier = []

        self.validation_window = tk.Toplevel(master)
        self.validation_window.title("Validation")
        self.validation_window.geometry("1400x1100")
        self.validation_window.grab_set()

        self.current_phase = 1

        self.not_classifier_page = 0
        self.not_classifier_per_page = 21
        self.total_not_classifier_pages = max(
            (len(self.not_classifier_images)-1)//self.not_classifier_per_page+1, 1
        )

        self.current_classifier_index = 0
        self.total_classifier = len(self.classifier_images)
        self.final_classifier_images = []

        self.phase1_frame = tk.Frame(self.validation_window)
        self.phase2_frame = tk.Frame(self.validation_window)

        self.setup_phase1()

    def get_thumbnail_image(self, filename, max_size):
        parent_folder = os.path.abspath(os.path.join(self.folder_path, ".."))
        thumbnails_folder = os.path.join(parent_folder, "thumbnails")

        if not os.path.exists(thumbnails_folder):
            os.makedirs(thumbnails_folder)
        thumb_filename = os.path.splitext(filename)[0] + "_thumb.jpg"
        thumb_path = os.path.join(thumbnails_folder, thumb_filename)
        if os.path.exists(thumb_path):
            thumb_img = Image.open(thumb_path).convert('RGB')
        else:
            original_path = os.path.join(self.folder_path, filename)
            thumb_img = Image.open(original_path).convert('RGB')
            thumb_img.thumbnail((max_size, max_size), Image.ANTIALIAS)
            thumb_img.save(thumb_path, format="JPEG")
        return thumb_img

    def setup_phase1(self):
        self.current_phase = 1
        self.phase1_frame.pack(fill='both', expand=True)

        title = tk.Label(
            self.phase1_frame,
            text=f"Phase 1: Validate {self.not_classifier_name} Images",
            font=("Helvetica", 16)
        )
        title.pack(pady=10)

        self.not_classifier_page_label = tk.Label(
            self.phase1_frame,
            font=("Helvetica", 12)
        )
        self.not_classifier_page_label.pack(pady=5)

        self.phase1_img_scale = tk.Scale(
            self.phase1_frame, from_=50, to=300, orient='horizontal',
            label="Image Size (px)"
        )
        self.phase1_img_scale.set(200)
        self.phase1_img_scale.pack(pady=5)

        canvas_container = tk.Frame(self.phase1_frame, height=600)
        canvas_container.pack(fill='x', padx=10, pady=5)
        canvas_container.pack_propagate(False)

        self.canvas = tk.Canvas(canvas_container, bg='white')
        self.scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grid_frame = tk.Frame(self.canvas, bg='white')
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0), window=self.grid_frame, anchor='nw')

        self.load_not_classifier_page()

        nav_frame = tk.Frame(self.phase1_frame)
        nav_frame.pack(pady=10)

        self.prev_button = tk.Button(
            nav_frame, text="Previous",
            command=self.prev_not_classifier_page, state='disabled'
        )
        self.prev_button.grid(row=0, column=0, padx=10)

        self.next_button = tk.Button(
            nav_frame, text="Next",
            command=self.next_not_classifier_page
        )
        self.next_button.grid(row=0, column=1, padx=10)

    def load_not_classifier_page(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        start = self.not_classifier_page * self.not_classifier_per_page
        end = start + self.not_classifier_per_page
        current_images = self.not_classifier_images[start:end]

        self.not_classifier_radio_vars = []

        rows, cols = 3, 7
        size = self.phase1_img_scale.get()
        for idx in range(rows):
            for jdx in range(cols):
                img_idx = idx * cols + jdx
                if img_idx >= len(current_images):
                    break
                img_info = current_images[img_idx]

                frame = tk.Frame(self.grid_frame, padx=5, pady=5, bg='white', bd=2, relief='groove')
                frame.grid(row=idx, column=jdx, padx=5, pady=5)

                try:
                    thumb_img = self.get_thumbnail_image(img_info['Filename'], size)
                    img_tk = ImageTk.PhotoImage(thumb_img)
                    label = tk.Label(frame, image=img_tk)
                    label.image = img_tk
                    label.pack()
                except Exception as e:
                    label = tk.Label(frame, text="Not Found", width=20, height=10, bg='grey')
                    label.pack()

                var = tk.IntVar(value=0)
                self.not_classifier_radio_vars.append(var)

                rb_not_classifier = tk.Radiobutton(frame, text=self.not_classifier_name, variable=var, value=0, bg='white')
                rb_not_classifier.pack(anchor='w')
                rb_classifier = tk.Radiobutton(frame, text=self.classifier_name, variable=var, value=1, bg='white')
                rb_classifier.pack(anchor='w')
                rb_exclude = tk.Radiobutton(frame, text="Exclude", variable=var, value=2, bg='white')
                rb_exclude.pack(anchor='w')

                confidence_text = img_info['Confidence']
                info_label = tk.Label(frame,
                    text=f"{img_info['Filename']}\nConf: {confidence_text}",
                    font=("Helvetica", 10), bg='white'
                )
                info_label.pack()

        self.not_classifier_page_label.config(
            text=f"Page {self.not_classifier_page+1} of {self.total_not_classifier_pages}"
        )

    def update_not_classifier_nav_buttons(self):
        self.prev_button.config(state='normal' if self.not_classifier_page > 0 else 'disabled')
        if self.not_classifier_page >= self.total_not_classifier_pages - 1:
            self.next_button.config(text="Proceed to Phase 2")
        else:
            self.next_button.config(text="Next")

    def prev_not_classifier_page(self):
        if self.not_classifier_page > 0:
            self.save_not_classifier_misclassifications()
            self.not_classifier_page -= 1
            self.load_not_classifier_page()
            self.update_not_classifier_nav_buttons()

    def next_not_classifier_page(self):
        self.save_not_classifier_misclassifications()
        if self.not_classifier_page < self.total_not_classifier_pages - 1:
            self.not_classifier_page += 1
            self.load_not_classifier_page()
        else:
            self.phase1_frame.pack_forget()
            self.setup_phase2()
        self.update_not_classifier_nav_buttons()

    def save_not_classifier_misclassifications(self):
        start = self.not_classifier_page * self.not_classifier_per_page
        end = start + self.not_classifier_per_page
        current_images = self.not_classifier_images[start:end]
        for idx, img_info in enumerate(current_images):
            val = self.not_classifier_radio_vars[idx].get()
            if val == 1:
                img_info['Classification'] = self.classifier_name
                self.misclassified_not_classifier.append(img_info)
            elif val == 2:
                img_info['Classification'] = 'Excluded'

    def setup_phase2(self):
        self.current_phase = 2
        self.phase2_frame.pack(fill='both', expand=True)

        title = tk.Label(
            self.phase2_frame,
            text=f"Phase 2: Validate {self.classifier_name} Images",
            font=("Helvetica", 16)
        )
        title.pack(pady=10)

        self.classifier_page_label = tk.Label(self.phase2_frame, font=("Helvetica", 12))
        self.classifier_page_label.pack(pady=5)

        self.phase2_img_scale = tk.Scale(
            self.phase2_frame, from_=100, to=900, orient='horizontal',
            label="Display Size (px)"
        )
        self.phase2_img_scale.set(700)
        self.phase2_img_scale.pack(pady=5)

        self.final_classifier_images = self.classifier_images + self.misclassified_not_classifier
        self.total_classifier = len(self.final_classifier_images)
        self.current_classifier_index = 0

        if self.total_classifier == 0:
            messagebox.showinfo(f"No {self.classifier_name} Images", f"No {self.classifier_name} images to validate.")
            self.generate_final_csv()
            return

        self.image_canvas = tk.Canvas(
            self.phase2_frame, width=700, height=700, bg='grey'
        )
        self.image_canvas.pack(pady=10)

        quick_frame = tk.Frame(self.phase2_frame)
        quick_frame.pack(pady=5)

        btn_all_classifier = tk.Button(quick_frame, text=f"All {self.classifier_name}", command=self.all_classifier)
        btn_all_classifier.grid(row=0, column=0, padx=5)

        btn_not_classifier = tk.Button(quick_frame, text=self.not_classifier_name, command=self.mark_not_classifier)
        btn_not_classifier.grid(row=0, column=1, padx=5)

        btn_exclude = tk.Button(quick_frame, text="Exclude", command=self.exclude_image)
        btn_exclude.grid(row=0, column=2, padx=5)

        self.selected_cells = {}
        self.load_classifier_image()

        nav_frame = tk.Frame(self.phase2_frame)
        nav_frame.pack(pady=10)

        self.prev_classifier_button = tk.Button(nav_frame, text="Previous", command=self.prev_classifier_image, state='disabled')
        self.prev_classifier_button.grid(row=0, column=0, padx=10)

        self.next_classifier_button = tk.Button(nav_frame, text="Next", command=self.next_classifier_image)
        self.next_classifier_button.grid(row=0, column=1, padx=10)

        self.generate_csv_button = tk.Button(
            self.phase2_frame, text="Generate CSV",
            command=self.generate_final_csv, bg="green", fg="white",
            font=("Helvetica", 12), width=20, height=2
        )
        self.generate_csv_button.pack(pady=10)

    def load_classifier_image(self):
        if not (0 <= self.current_classifier_index < self.total_classifier):
            return
        self.current_image_info = self.final_classifier_images[self.current_classifier_index]
        filename = self.current_image_info['Filename']

        self.image_canvas.delete("all")

        size = self.phase2_img_scale.get()
        try:
            thumb_img = self.get_thumbnail_image(filename, size)
            thumb_img = thumb_img.resize((size, size), Image.ANTIALIAS)
            self.img_tk = ImageTk.PhotoImage(thumb_img)
            self.image_canvas.create_image(0, 0, anchor='nw', image=self.img_tk)
        except Exception as e:
            self.image_canvas.create_text(
                size//2, size//2,
                text="Not Found", fill="white", font=("Helvetica",20)
            )

        self.cell_size = size // 10 if size >= 10 else 1
        self.grid = []
        for i in range(10):
            for j in range(10):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.image_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline='white', tags="grid", fill=''
                )
                self.grid.append(rect)

        if filename not in self.selected_cells:
            self.selected_cells[filename] = set()

        self.update_grid_selection()
        self.image_canvas.bind("<Button-1>", self.on_canvas_click)
        self.image_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.classifier_page_label.config(text=f"Image {self.current_classifier_index+1} of {self.total_classifier}")

    def update_grid_selection(self):
        filename = self.current_image_info['Filename']
        selected = self.selected_cells.get(filename, set())
        for idx in range(100):
            if idx in selected:
                self.image_canvas.itemconfig(self.grid[idx], fill='blue', stipple='gray25')
            else:
                self.image_canvas.itemconfig(self.grid[idx], fill='')

    def on_canvas_click(self, event):
        self.handle_selection(event, single_click=True)

    def on_canvas_drag(self, event):
        self.handle_selection(event, single_click=False)

    def handle_selection(self, event, single_click=True):
        x, y = event.x, event.y
        col = x // self.cell_size
        row = y // self.cell_size
        if not (0 <= col < 10 and 0 <= row < 10):
            return
        idx = row * 10 + col
        filename = self.current_image_info['Filename']
        if single_click:
            if idx in self.selected_cells[filename]:
                self.selecting = False
                self.selected_cells[filename].remove(idx)
            else:
                self.selecting = True
                self.selected_cells[filename].add(idx)
            self.last_toggled_cell = idx
        else:
            if hasattr(self, 'last_toggled_cell') and idx == self.last_toggled_cell:
                return
            self.last_toggled_cell = idx
            if self.selecting:
                self.selected_cells[filename].add(idx)
            else:
                self.selected_cells[filename].discard(idx)
        self.update_grid_selection()

    def prev_classifier_image(self):
        if self.current_classifier_index > 0:
            self.save_classifier_cover()
            self.current_classifier_index -= 1
            self.load_classifier_image()
            self.next_classifier_button.config(state='normal')
        if self.current_classifier_index == 0:
            self.prev_classifier_button.config(state='disabled')

    def next_classifier_image(self):
        self.save_classifier_cover()
        if self.current_classifier_index < self.total_classifier - 1:
            self.current_classifier_index += 1
            self.load_classifier_image()
            self.prev_classifier_button.config(state='normal')
        else:
            self.next_classifier_button.config(state='disabled')

    def save_classifier_cover(self):
        filename = self.current_image_info['Filename']
        selected = len(self.selected_cells.get(filename, set()))
        percent_classifier = f"{(selected / 100) * 100:.2f}%"
        for img in self.results:
            if img['Filename'] == filename:
                img[f'Percent {self.classifier_name} Cover'] = percent_classifier
                break
        try:
            original_img_path = os.path.join(self.folder_path, filename)
            original_img = Image.open(original_img_path).convert('RGB')
            width, height = original_img.size
            mask_array = np.zeros((height, width), dtype=np.uint8)
            cell_width = width // 10
            cell_height = height // 10
            selected_cells = self.selected_cells.get(filename, set())
            for i in range(10):
                for j in range(10):
                    cell_index = i * 10 + j
                    if cell_index in selected_cells:
                        left = j * cell_width
                        right = left + cell_width if j < 9 else width
                        upper = i * cell_height
                        lower = upper + cell_height if i < 9 else height
                        mask_array[upper:lower, left:right] = 255
            mask_img = Image.fromarray(mask_array)
            mask_img.thumbnail((300, 300), Image.ANTIALIAS)
            parent_folder = os.path.abspath(os.path.join(self.folder_path, ".."))
            masks_folder = os.path.join(parent_folder, "masks")
            if not os.path.exists(masks_folder):
                os.makedirs(masks_folder)
            mask_filename = os.path.splitext(filename)[0] + ".png"
            mask_img.save(os.path.join(masks_folder, mask_filename))
        except Exception as e:
            print(f"Failed to save mask for {filename}: {e}")

    def all_classifier(self):
        filename = self.current_image_info['Filename']
        self.selected_cells[filename] = set(range(100))
        self.update_grid_selection()

    def mark_not_classifier(self):
        filename = self.current_image_info['Filename']
        self.selected_cells[filename] = set()
        self.update_grid_selection()
        for img in self.results:
            if img['Filename'] == filename:
                img['Classification'] = self.not_classifier_name
                img[f'Percent {self.classifier_name} Cover'] = "N/A"
                break

    def exclude_image(self):
        filename = self.current_image_info['Filename']
        for img in self.results:
            if img['Filename'] == filename:
                img['Classification'] = "Excluded"
                img[f'Percent {self.classifier_name} Cover'] = "N/A"
                break
        self.next_classifier_image()

    def generate_final_csv(self):
        try:
            fieldnames = ['Filename', 'Classification', 'Confidence', f'Percent {self.classifier_name} Cover']
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.results:
                    writer.writerow(row)
            messagebox.showinfo("Success", f"Validation complete!\nSaved: {self.csv_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write CSV.\n{e}")
        finally:
            self.validation_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
