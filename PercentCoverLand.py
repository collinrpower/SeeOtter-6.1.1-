import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np
import os
import csv
from datetime import datetime
import threading

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'best_model.keras')

try:
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
except Exception as e:
    messagebox.showerror("Error", f"Failed to load the model.\n{e}")
    exit()

class_names = ['Land','Water']

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
        self.master.title("Land vs Water Image Classifier")
        self.master.geometry("600x300")
        self.master.resizable(False, False)

        self.frame = tk.Frame(self.master, padx=20, pady=20)
        self.frame.pack(expand=True, fill='both')

        self.instruction_label = tk.Label(
            self.frame,
            text="Upload a folder of images to classify as Land or Water.",
            font=("Helvetica", 14)
        )
        self.instruction_label.pack(pady=10)

        self.upload_button = tk.Button(
            self.frame,
            text="Upload Folder",
            command=self.upload_and_predict_folder,
            bg="blue",
            fg="white",
            font=("Helvetica", 12),
            width=20,
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

    def upload_and_predict_folder(self):
        self.folder_path = filedialog.askdirectory(
            title="Select Folder Containing Images"
        )
        if self.folder_path:
            supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
            image_files = [
                f for f in os.listdir(self.folder_path)
                if f.lower().endswith(supported_extensions)
            ]

            if not image_files:
                messagebox.showinfo("No Images", "No supported image files found.")
                return

            default_csv_name = f"classifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=default_csv_name,
                filetypes=[("CSV Files", "*.csv")]
            )
            if not csv_path:
                return

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
                        'Percent Land Cover': 'N/A'
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

                    predictions = model.predict(batch_images)

                    for filename, prediction in zip(batch_filenames, predictions):
                        predicted_label = int(prediction > 0.5)
                        predicted_class = class_names[predicted_label]
                        confidence = prediction[0]
                        self.results.append({
                            'Filename': filename,
                            'Classification': predicted_class,
                            'Confidence': f"{confidence * 100:.2f}%",
                            'Percent Land Cover': 'N/A'
                        })
                    processed = min(end, len(preprocessed_images))
                    self.progress_label.config(text=f"Classifying {processed}/{total}...")
                    self.progress_bar['value'] = processed
                    self.master.update_idletasks()

            self.progress_label.config(text="Processing complete. Launching validation...")
            self.master.update_idletasks()
            ValidationWindow(self.master, self.results, csv_path, folder_path)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred.\n{e}")
        finally:
            self.upload_button.config(state='normal')
            self.progress_label.config(text="Processing complete.")
            self.progress_bar['value'] = 0

class ValidationWindow:
    def __init__(self, master, results, csv_path, folder_path):
        self.master = master
        self.results = results
        self.csv_path = csv_path
        self.folder_path = folder_path

        self.water_images = [
            img for img in self.results
            if img['Classification'] == 'Water'
        ]
        self.water_images.sort(
            key=lambda x: float(x['Confidence'].replace('%','')) if x['Confidence'] != 'N/A' else 0
        )

        self.land_images = [
            img for img in self.results
            if img['Classification'] == 'Land'
        ]

        self.misclassified_water = []

        self.validation_window = tk.Toplevel(master)
        self.validation_window.title("Validation")
        self.validation_window.geometry("1400x1100")
        self.validation_window.grab_set()

        self.current_phase = 1

        self.water_page = 0
        self.water_per_page = 21
        self.total_water_pages = max((len(self.water_images)-1)//self.water_per_page+1,1)

        self.current_land_index = 0
        self.total_land = len(self.land_images)
        self.final_land_images = []

        self.phase1_frame = tk.Frame(self.validation_window)
        self.phase2_frame = tk.Frame(self.validation_window)

        self.setup_phase1()

    # ----------------------- PHASE 1 -----------------------
    def setup_phase1(self):
        self.current_phase = 1
        self.phase1_frame.pack(fill='both', expand=True)

        title = tk.Label(
            self.phase1_frame,
            text="Phase 1: Validate Water Images",
            font=("Helvetica",16)
        )
        title.pack(pady=10)

        self.water_page_label = tk.Label(
            self.phase1_frame,
            text=f"Page {self.water_page+1} of {self.total_water_pages}",
            font=("Helvetica",12)
        )
        self.water_page_label.pack(pady=5)

        # Scale to adjust image size
        self.phase1_img_scale = tk.Scale(
            self.phase1_frame, from_=50, to=300, orient='horizontal',
            label="Image Size (px)"
        )
        self.phase1_img_scale.set(200)
        self.phase1_img_scale.pack(pady=5)

        # Container frame with fixed height
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

        self.load_water_page()

        nav_frame = tk.Frame(self.phase1_frame)
        nav_frame.pack(pady=10)

        self.prev_button = tk.Button(
            nav_frame, text="Previous",
            command=self.prev_water_page, state='disabled'
        )
        self.prev_button.grid(row=0, column=0, padx=10)

        self.next_button = tk.Button(
            nav_frame, text="Next",
            command=self.next_water_page
        )
        self.next_button.grid(row=0, column=1, padx=10)

    def load_water_page(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        start = self.water_page * self.water_per_page
        end = start + self.water_per_page
        current_images = self.water_images[start:end]

        self.water_radio_vars = []

        rows, cols = 3, 7
        size = self.phase1_img_scale.get()
        for idx in range(rows):
            for jdx in range(cols):
                img_idx = idx*cols + jdx
                if img_idx >= len(current_images):
                    break
                img_info = current_images[img_idx]

                frame = tk.Frame(self.grid_frame, padx=5, pady=5, bg='white', bd=2, relief='groove')
                frame.grid(row=idx, column=jdx, padx=5, pady=5)

                try:
                    img_path = os.path.join(self.folder_path, img_info['Filename'])
                    img = Image.open(img_path).convert('RGB')
                    img = img.resize((size, size))
                    img_tk = ImageTk.PhotoImage(img)
                    label = tk.Label(frame, image=img_tk)
                    label.image = img_tk
                    label.pack()
                except:
                    label = tk.Label(frame, text="Not Found", width=20, height=10, bg='grey')
                    label.pack()

                var = tk.IntVar(value=0)  # 0=Water,1=Land,2=Exclude
                self.water_radio_vars.append(var)

                rb_water = tk.Radiobutton(frame, text="Water", variable=var, value=0, bg='white')
                rb_water.pack(anchor='w')
                rb_land = tk.Radiobutton(frame, text="Land", variable=var, value=1, bg='white')
                rb_land.pack(anchor='w')
                rb_exclude = tk.Radiobutton(frame, text="Exclude", variable=var, value=2, bg='white')
                rb_exclude.pack(anchor='w')

                confidence_text = img_info['Confidence']
                info_label = tk.Label(frame,
                    text=f"{img_info['Filename']}\nConf: {confidence_text}",
                    font=("Helvetica",10), bg='white'
                )
                info_label.pack()

        self.water_page_label.config(
            text=f"Page {self.water_page+1} of {self.total_water_pages}"
        )

    def update_water_nav_buttons(self):
        self.prev_button.config(state='normal' if self.water_page>0 else 'disabled')
        if self.water_page >= self.total_water_pages-1:
            self.next_button.config(text="Proceed to Phase 2")
        else:
            self.next_button.config(text="Next")

    def prev_water_page(self):
        if self.water_page>0:
            self.save_water_misclassifications()
            self.water_page -=1
            self.load_water_page()
            self.update_water_nav_buttons()

    def next_water_page(self):
        self.save_water_misclassifications()
        if self.water_page < self.total_water_pages-1:
            self.water_page +=1
            self.load_water_page()
        else:
            self.phase1_frame.pack_forget()
            self.setup_phase2()
        self.update_water_nav_buttons()

    def save_water_misclassifications(self):
        start = self.water_page*self.water_per_page
        end = start + self.water_per_page
        current_images = self.water_images[start:end]
        for idx, img_info in enumerate(current_images):
            val = self.water_radio_vars[idx].get()
            if val==1:
                img_info['Classification'] = 'Land'
                self.misclassified_water.append(img_info)
            elif val==2:
                img_info['Classification'] = 'Excluded'

    # ----------------------- PHASE 2 -----------------------
    def setup_phase2(self):
        self.current_phase = 2
        self.phase2_frame.pack(fill='both', expand=True)

        title = tk.Label(
            self.phase2_frame,
            text="Phase 2: Validate Land Images",
            font=("Helvetica",16)
        )
        title.pack(pady=10)

        self.land_page_label = tk.Label(self.phase2_frame, font=("Helvetica",12))
        self.land_page_label.pack(pady=5)

        # Scale for resizing
        self.phase2_img_scale = tk.Scale(
            self.phase2_frame, from_=100, to=900, orient='horizontal',
            label="Display Size (px)"
        )
        self.phase2_img_scale.set(700)
        self.phase2_img_scale.pack(pady=5)

        self.final_land_images = self.land_images + self.misclassified_water
        self.total_land = len(self.final_land_images)
        self.current_land_index = 0

        if self.total_land == 0:
            messagebox.showinfo("No Land Images", "No land images to validate.")
            self.generate_final_csv()
            return

        self.image_canvas = tk.Canvas(
            self.phase2_frame, width=700, height=700, bg='grey'
        )
        self.image_canvas.pack(pady=10)

        # Buttons for quick selection
        quick_frame = tk.Frame(self.phase2_frame)
        quick_frame.pack(pady=5)

        btn_all_land = tk.Button(quick_frame, text="All Land", command=self.all_land)
        btn_all_land.grid(row=0, column=0, padx=5)

        btn_water = tk.Button(quick_frame, text="Water", command=self.mark_water)
        btn_water.grid(row=0, column=1, padx=5)

        btn_exclude = tk.Button(quick_frame, text="Exclude", command=self.exclude_image)
        btn_exclude.grid(row=0, column=2, padx=5)

        self.selected_cells = {}
        self.load_land_image()

        nav_frame = tk.Frame(self.phase2_frame)
        nav_frame.pack(pady=10)

        self.prev_land_button = tk.Button(nav_frame, text="Previous", command=self.prev_land_image, state='disabled')
        self.prev_land_button.grid(row=0, column=0, padx=10)

        self.next_land_button = tk.Button(nav_frame, text="Next", command=self.next_land_image)
        self.next_land_button.grid(row=0, column=1, padx=10)

        self.generate_csv_button = tk.Button(
            self.phase2_frame, text="Generate CSV",
            command=self.generate_final_csv, bg="green", fg="white",
            font=("Helvetica",12), width=20, height=2
        )
        self.generate_csv_button.pack(pady=10)

    def load_land_image(self):
        if not (0 <= self.current_land_index < self.total_land):
            return
        self.current_image_info = self.final_land_images[self.current_land_index]
        filename = self.current_image_info['Filename']

        self.image_canvas.delete("all")

        size = self.phase2_img_scale.get()
        try:
            img_path = os.path.join(self.folder_path, filename)
            img = Image.open(img_path).convert('RGB')
            img = img.resize((size, size))
            self.img_tk = ImageTk.PhotoImage(img)
            self.image_canvas.create_image(0, 0, anchor='nw', image=self.img_tk)
        except:
            self.image_canvas.create_text(
                350, 350, text="Not Found",
                fill="white", font=("Helvetica",20)
            )

        self.cell_size = size//10 if size>=10 else 1
        self.grid = []
        for i in range(10):
            for j in range(10):
                x1 = j*self.cell_size
                y1 = i*self.cell_size
                x2 = x1+self.cell_size
                y2 = y1+self.cell_size
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
        self.land_page_label.config(text=f"Image {self.current_land_index+1} of {self.total_land}")

    def update_grid_selection(self):
        filename = self.current_image_info['Filename']
        selected = self.selected_cells.get(filename,set())
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
        col = x//self.cell_size
        row = y//self.cell_size
        if not(0<=col<10 and 0<=row<10):
            return
        idx = row*10 + col
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
            if hasattr(self,'last_toggled_cell') and idx==self.last_toggled_cell:
                return
            self.last_toggled_cell = idx
            if self.selecting:
                self.selected_cells[filename].add(idx)
            else:
                self.selected_cells[filename].discard(idx)
        self.update_grid_selection()

    def prev_land_image(self):
        if self.current_land_index>0:
            self.save_land_cover()
            self.current_land_index-=1
            self.load_land_image()
            self.next_land_button.config(state='normal')
        if self.current_land_index==0:
            self.prev_land_button.config(state='disabled')

    def next_land_image(self):
        self.save_land_cover()
        if self.current_land_index<self.total_land-1:
            self.current_land_index+=1
            self.load_land_image()
            self.prev_land_button.config(state='normal')
        else:
            self.next_land_button.config(state='disabled')

    def save_land_cover(self):
        filename = self.current_image_info['Filename']
        selected = len(self.selected_cells.get(filename, set()))
        percent_land = f"{(selected/100)*100:.2f}%"
        for img in self.results:
            if img['Filename'] == filename:
                img['Percent Land Cover'] = percent_land
                break

    # ---- Quick Buttons in Phase 2 ----
    def all_land(self):
        filename = self.current_image_info['Filename']
        self.selected_cells[filename] = set(range(100))
        self.update_grid_selection()

    def mark_water(self):
        filename = self.current_image_info['Filename']
        # Clear selection
        self.selected_cells[filename] = set()
        self.update_grid_selection()
        # Update classification
        for img in self.results:
            if img['Filename'] == filename:
                img['Classification'] = "Water"
                img['Percent Land Cover'] = "N/A"
                break

    def exclude_image(self):
        filename = self.current_image_info['Filename']
        for img in self.results:
            if img['Filename'] == filename:
                img['Classification'] = "Excluded"
                img['Percent Land Cover'] = "N/A"
                break
        self.next_land_image()

    def generate_final_csv(self):
        try:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csv_file:
                fieldnames = ['Filename','Classification','Confidence','Percent Land Cover']
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
