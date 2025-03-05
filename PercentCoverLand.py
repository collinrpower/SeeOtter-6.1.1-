import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np
import os
import csv
from datetime import datetime
import threading
import queue
import concurrent.futures
import logging
import stat
import math

# Fallback for Pillow resampling (compatibility with older versions)
try:
    resample_method = Image.Resampling.LANCZOS
except AttributeError:
    resample_method = Image.LANCZOS

# ------------------------- LOGGING SETUP -------------------------
logging.basicConfig(
    filename='app_log.txt',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ------------------------- MODEL LOADING (ASYNC) -------------------------
class_names = ['Land', 'Water']
model = None
model_load_queue = queue.Queue()

def load_model_async(model_path):
    try:
        loaded_model = tf.keras.models.load_model(model_path, compile=False)
        loaded_model.compile(
            optimizer=tf.keras.optimizers.Adam(),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        model_load_queue.put(('done', loaded_model))
    except Exception as e:
        logging.error("Model load failed", exc_info=True)
        model_load_queue.put(('error', str(e)))

# ------------------------- IMAGE PROCESSING -------------------------
def can_read_file(file_path):
    try:
        st = os.stat(file_path)
        return bool(st.st_mode & stat.S_IRUSR)
    except Exception:
        return False

def save_thumbnail(pil_img, thumbnail_folder, original_filename):
    os.makedirs(thumbnail_folder, exist_ok=True)
    base, _ = os.path.splitext(os.path.basename(original_filename))
    thumb_filename = base + "_thumb.png"
    thumb_path = os.path.join(thumbnail_folder, thumb_filename)
    try:
        pil_img.save(thumb_path, format="PNG")
        return thumb_path
    except Exception as e:
        logging.error("Failed to save thumbnail", exc_info=True)
        return ""

def preprocess_image(image_path, target_size=(128, 128)):
    try:
        pil_img = Image.open(image_path).convert('RGB')
        pil_img = pil_img.resize(target_size, resample_method)
        img_array = np.array(pil_img) / 255.0
        return img_array, pil_img
    except Exception:
        return None, None

# ------------------------- MAIN APPLICATION -------------------------
class MainApplication:
    def __init__(self, master, model_path='best_model.keras'):
        self.master = master
        self.master.title("Land vs Water Image Classifier")
        self.master.geometry("600x300")
        self.master.minsize(500, 250)

        threading.Thread(target=load_model_async, args=(model_path,), daemon=True).start()

        self.frame = tk.Frame(self.master, padx=20, pady=20)
        self.frame.pack(expand=True, fill='both')

        self.instruction_label = tk.Label(
            self.frame,
            text="Loading model, please wait...",
            font=("Helvetica", 14)
        )
        self.instruction_label.pack(pady=10)

        self.upload_button = tk.Button(
            self.frame,
            text="Upload Folder",
            command=self.upload_and_predict_folder,
            bg="blue", fg="white",
            font=("Helvetica", 12),
            width=20, height=2,
            state='disabled'
        )
        self.upload_button.pack(pady=10)

        self.progress_bar = ttk.Progressbar(
            self.frame,
            orient='horizontal',
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)

        self.progress_label = tk.Label(self.frame, text="", font=("Helvetica", 12))
        self.progress_label.pack(pady=5)

        self.help_button = tk.Button(
            self.frame,
            text="Help",
            command=self.show_help
        )
        self.help_button.pack()

        self.master.after(200, self.check_model_loaded)

        self.folder_path = ""
        self.csv_path = ""
        self.image_files = []
        self.worker_queue = queue.Queue()

    def check_model_loaded(self):
        try:
            while True:
                msg = model_load_queue.get_nowait()
                if msg[0] == 'done':
                    global model
                    model = msg[1]
                    self.instruction_label.config(text="Model loaded. Select a folder to begin.")
                    self.upload_button.config(state='normal')
                elif msg[0] == 'error':
                    err = msg[1]
                    messagebox.showerror("Error", f"Failed to load the model.\n{err}")
                    self.instruction_label.config(text="Model loading failed. Check app_log.txt for details.")
                break
        except queue.Empty:
            pass
        if model is None:
            self.master.after(200, self.check_model_loaded)

    def show_help(self):
        help_win = tk.Toplevel(self.master)
        help_win.title("Help")
        help_label = tk.Label(
            help_win,
            text=(
                "1) Wait for the model to load.\n"
                "2) Click 'Upload Folder' to choose your images.\n"
                "3) Wait for preprocessing and classification to finish.\n"
                "4) Validate Water images in Phase 1.\n"
                "5) Validate Land images in Phase 2.\n"
                "6) Generate a CSV with final results.\n"
            ),
            font=("Helvetica", 12),
            padx=10, pady=10
        )
        help_label.pack()

    def upload_and_predict_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
        if not folder_path:
            return

        supported_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        raw_files = os.listdir(folder_path)
        image_files = [
            f for f in raw_files
            if f.lower().endswith(supported_exts) and can_read_file(os.path.join(folder_path, f))
        ]
        if not image_files:
            messagebox.showinfo("No Images", "No readable or supported image files found.")
            return

        default_csv_name = f"classifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_csv_name,
            filetypes=[("CSV Files", "*.csv")]
        )
        if not csv_path:
            return

        self.folder_path = folder_path
        self.csv_path = csv_path
        self.image_files = image_files

        self.upload_button.config(state='disabled')
        self.progress_label.config(text="Starting processing...")
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(image_files)

        threading.Thread(target=self.process_images_worker, daemon=True).start()
        self.master.after(100, self.check_worker_queue)

    def process_images_worker(self):
        results = []
        folder_path = self.folder_path
        image_files = self.image_files
        total = len(image_files)
        processed_count = 0
        thumbnail_folder = os.path.join(folder_path, "_thumbnails")
        chunk_size = 500

        for chunk_start in range(0, total, chunk_size):
            chunk_files = image_files[chunk_start:chunk_start+chunk_size]
            preprocessed_arrays = []
            valid_files = []
            thumbnail_paths = []

            max_workers = min(32, os.cpu_count() or 4)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(preprocess_image, os.path.join(folder_path, f)): f for f in chunk_files}
                for future in concurrent.futures.as_completed(future_to_file):
                    filename = future_to_file[future]
                    try:
                        img_arr, pil_img = future.result()
                        if img_arr is not None and pil_img is not None:
                            preprocessed_arrays.append(img_arr)
                            valid_files.append(filename)
                            thumb_path = save_thumbnail(pil_img, thumbnail_folder, filename)
                            thumbnail_paths.append(thumb_path)
                        else:
                            results.append({
                                'Filename': filename,
                                'Classification': 'Error',
                                'Confidence': 'N/A',
                                'Percent Land Cover': 'N/A',
                                'ThumbnailPath': ''
                            })
                    except Exception:
                        results.append({
                            'Filename': filename,
                            'Classification': 'Error',
                            'Confidence': 'N/A',
                            'Percent Land Cover': 'N/A',
                            'ThumbnailPath': ''
                        })
                    processed_count += 1
                    self.worker_queue.put(('progress', f"Preprocessing ({processed_count}/{total})", processed_count))

            if preprocessed_arrays:
                preprocessed_arrays = np.array(preprocessed_arrays)
                preds = []
                batch_size = 32
                class_processed = 0
                for i in range(0, len(preprocessed_arrays), batch_size):
                    batch = preprocessed_arrays[i:i+batch_size]
                    batch_preds = model.predict(batch, batch_size=batch_size)
                    preds.extend(batch_preds)
                    class_processed += len(batch_preds)
                    self.worker_queue.put(('progress', f"Classifying ({class_processed}/{len(preprocessed_arrays)})", processed_count))
                for filename, pred, thumb in zip(valid_files, preds, thumbnail_paths):
                    conf = float(pred)
                    label_idx = int(conf > 0.5)
                    cls = class_names[label_idx]
                    results.append({
                        'Filename': filename,
                        'Classification': cls,
                        'Confidence': f"{conf * 100:.2f}%",
                        'Percent Land Cover': 'N/A',
                        'ThumbnailPath': thumb
                    })

        self.worker_queue.put(('done', results))

    def check_worker_queue(self):
        try:
            while True:
                msg = self.worker_queue.get_nowait()
                if msg[0] == 'progress':
                    self.progress_label.config(text=msg[1])
                    self.progress_bar['value'] = msg[2]
                elif msg[0] == 'done':
                    self.finish_processing(msg[1])
                elif msg[0] == 'error':
                    err_msg = msg[1]
                    messagebox.showerror("Error", f"An error occurred.\n{err_msg}")
                    self.upload_button.config(state='normal')
                    self.progress_label.config(text="")
                    self.progress_bar['value'] = 0
        except queue.Empty:
            pass
        self.master.after(100, self.check_worker_queue)

    def finish_processing(self, results):
        self.upload_button.config(state='normal')
        self.progress_label.config(text="Processing complete. Launching validation...")
        self.progress_bar['value'] = 0
        ValidationWindow(self.master, results, self.csv_path, self.folder_path)

# ------------------------- VALIDATION WINDOW -------------------------
class ValidationWindow:
    def __init__(self, master, results, csv_path, folder_path):
        self.master = master
        self.results = results
        self.csv_path = csv_path
        self.folder_path = folder_path

        self.water_images = [r for r in results if r['Classification'] == 'Water']
        self.water_images.sort(
            key=lambda x: float(x['Confidence'].replace('%','')) if x['Confidence'] != 'N/A' else 0
        )
        self.land_images = [r for r in results if r['Classification'] == 'Land']
        self.misclassified_water = []

        # Pagination variables for Phase 1
        self.water_page = 0
        self.water_images_per_page = 250
        self.total_water_pages = math.ceil(len(self.water_images) / self.water_images_per_page)

        self.validation_window = tk.Toplevel(master)
        self.validation_window.title("Validation")
        self.validation_window.geometry("1400x1100")
        self.validation_window.grab_set()

        self.phase1_frame = tk.Frame(self.validation_window)
        self.phase2_frame = tk.Frame(self.validation_window)

        self.setup_phase1()

    def setup_phase1(self):
        self.phase1_frame.pack(fill='both', expand=True)

        tk.Label(
            self.phase1_frame,
            text="Phase 1: Validate Water Images",
            font=("Helvetica",16)
        ).pack(pady=10)

        tk.Label(
            self.phase1_frame,
            text=f"Total Water Images: {len(self.water_images)}",
            font=("Helvetica",12)
        ).pack(pady=5)

        self.phase1_img_scale = tk.Scale(
            self.phase1_frame, from_=50, to=300, orient='horizontal',
            label="Image Size (px)"
        )
        self.phase1_img_scale.set(200)
        self.phase1_img_scale.pack(pady=5)

        canvas_container = tk.Frame(self.phase1_frame)
        canvas_container.pack(fill='both', expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(canvas_container, bg='white')
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.grid_frame = tk.Frame(self.canvas, bg='white')
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor='nw')

        self.canvas.bind("<Enter>", lambda e: self._bind_canvas_scroll())
        self.canvas.bind("<Leave>", lambda e: self._unbind_canvas_scroll())

        self.water_radio_vars = []
        self.load_all_water_images()

        # Pagination controls
        pagination_frame = tk.Frame(self.phase1_frame)
        pagination_frame.pack(pady=5)
        self.prev_page_button = tk.Button(pagination_frame, text="<< Previous", command=self.prev_water_page)
        self.prev_page_button.grid(row=0, column=0, padx=5)
        self.page_label = tk.Label(pagination_frame, text=f"Page {self.water_page+1} of {self.total_water_pages}", font=("Helvetica",12))
        self.page_label.grid(row=0, column=1, padx=5)
        self.next_page_button = tk.Button(pagination_frame, text="Next >>", command=self.next_water_page)
        self.next_page_button.grid(row=0, column=2, padx=5)
        self.update_pagination_buttons()

        self.move_excluded_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.phase1_frame,
            text="Move Excluded Files to a separate 'excluded' folder",
            variable=self.move_excluded_var
        ).pack(pady=5)

        tk.Button(
            self.phase1_frame,
            text="Proceed to Phase 2",
            command=self.proceed_to_phase2
        ).pack(pady=10)

    def _bind_canvas_scroll(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_canvas_scroll(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if hasattr(event, 'delta') and event.delta:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def load_all_water_images(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.water_radio_vars = []  # reset radio variables

        size = self.phase1_img_scale.get()
        cols = 7
        start_index = self.water_page * self.water_images_per_page
        end_index = start_index + self.water_images_per_page
        page_images = self.water_images[start_index:end_index]

        for idx, img_info in enumerate(page_images):
            row = idx // cols
            col = idx % cols
            frame = tk.Frame(self.grid_frame, padx=5, pady=5, bg='white', bd=2, relief='groove')
            frame.grid(row=row, column=col, padx=5, pady=5)

            thumb_path = img_info.get('ThumbnailPath', '')
            pil_img = None
            if thumb_path and os.path.isfile(thumb_path):
                try:
                    pil_img = Image.open(thumb_path).convert('RGB')
                    pil_img = pil_img.resize((size, size), resample_method)
                except Exception:
                    pil_img = None
            if pil_img is None:
                try:
                    original_path = os.path.join(self.folder_path, img_info['Filename'])
                    pil_img = Image.open(original_path).convert('RGB')
                    pil_img = pil_img.resize((size, size), resample_method)
                except Exception:
                    pil_img = None
            if pil_img:
                tk_img = ImageTk.PhotoImage(pil_img)
                lbl = tk.Label(frame, image=tk_img)
                lbl.image = tk_img
                lbl.pack()
            else:
                tk.Label(frame, text="Error loading", width=20, height=10, bg='grey').pack()

            var = tk.IntVar(value=0)
            self.water_radio_vars.append(var)
            tk.Radiobutton(frame, text="Water", variable=var, value=0, bg='white').pack(anchor='w')
            tk.Radiobutton(frame, text="Land", variable=var, value=1, bg='white').pack(anchor='w')
            tk.Radiobutton(frame, text="Exclude", variable=var, value=2, bg='white').pack(anchor='w')
            tk.Label(
                frame,
                text=f"{img_info['Filename']}\nConf: {img_info['Confidence']}",
                font=("Helvetica",10), bg='white'
            ).pack()

    def next_water_page(self):
        if self.water_page < self.total_water_pages - 1:
            self.water_page += 1
            self.load_all_water_images()
            self.page_label.config(text=f"Page {self.water_page+1} of {self.total_water_pages}")
            self.update_pagination_buttons()

    def prev_water_page(self):
        if self.water_page > 0:
            self.water_page -= 1
            self.load_all_water_images()
            self.page_label.config(text=f"Page {self.water_page+1} of {self.total_water_pages}")
            self.update_pagination_buttons()

    def update_pagination_buttons(self):
        self.prev_page_button.config(state='normal' if self.water_page > 0 else 'disabled')
        self.next_page_button.config(state='normal' if self.water_page < self.total_water_pages - 1 else 'disabled')

    def proceed_to_phase2(self):
        excluded_count = 0
        changed_to_land_count = 0

        for idx, img_info in enumerate(self.water_images):
            val = self.water_radio_vars[idx % self.water_images_per_page].get()  # account for pagination
            if val == 1:
                img_info['Classification'] = 'Land'
                self.misclassified_water.append(img_info)
                changed_to_land_count += 1
            elif val == 2:
                img_info['Classification'] = 'Excluded'
                excluded_count += 1

        msg = (
            f"Changed from Water to Land: {changed_to_land_count}\n"
            f"Excluded: {excluded_count}"
        )
        messagebox.showinfo("Phase 1 Summary", msg)

        if self.move_excluded_var.get():
            excluded_folder = os.path.join(self.folder_path, "excluded")
            os.makedirs(excluded_folder, exist_ok=True)
            for img in self.water_images:
                if img['Classification'] == 'Excluded':
                    src = os.path.join(self.folder_path, img['Filename'])
                    dst = os.path.join(excluded_folder, img['Filename'])
                    if os.path.isfile(src):
                        try:
                            os.rename(src, dst)
                        except Exception:
                            logging.error(f"Failed to move excluded file {src}", exc_info=True)

        self.phase1_frame.pack_forget()
        self.setup_phase2()

    def setup_phase2(self):
        self.phase2_frame.pack(fill='both', expand=True)
        tk.Label(self.phase2_frame, text="Phase 2: Validate Land Images", font=("Helvetica",16)).pack(pady=10)

        self.land_page_label = tk.Label(self.phase2_frame, font=("Helvetica",12))
        self.land_page_label.pack(pady=5)

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

        self.image_canvas = tk.Canvas(self.phase2_frame, width=700, height=700, bg='grey')
        self.image_canvas.pack(pady=10)

        quick_frame = tk.Frame(self.phase2_frame)
        quick_frame.pack(pady=5)
        tk.Button(quick_frame, text="All Land", command=self.all_land).grid(row=0, column=0, padx=5)
        tk.Button(quick_frame, text="Water", command=self.mark_water).grid(row=0, column=1, padx=5)
        tk.Button(quick_frame, text="Exclude", command=self.exclude_image).grid(row=0, column=2, padx=5)

        self.selected_cells = {}
        self.load_land_image()

        nav_frame = tk.Frame(self.phase2_frame)
        nav_frame.pack(pady=10)
        self.prev_land_button = tk.Button(nav_frame, text="Previous", command=self.prev_land_image, state='disabled')
        self.prev_land_button.grid(row=0, column=0, padx=10)
        self.next_land_button = tk.Button(nav_frame, text="Next", command=self.next_land_image)
        self.next_land_button.grid(row=0, column=1, padx=10)

        self.generate_csv_button = tk.Button(
            self.phase2_frame,
            text="Generate CSV",
            command=self.generate_final_csv,
            bg="green", fg="white",
            font=("Helvetica",12), width=20, height=2
        )
        self.generate_csv_button.pack(pady=10)

    def load_land_image(self):
        if not (0 <= self.current_land_index < self.total_land):
            return
        self.current_image_info = self.final_land_images[self.current_land_index]
        filename = self.current_image_info['Filename']
        thumb_path = self.current_image_info.get('ThumbnailPath', '')

        self.image_canvas.delete("all")
        size = self.phase2_img_scale.get()
        pil_img = None
        if thumb_path and os.path.isfile(thumb_path):
            try:
                pil_img = Image.open(thumb_path).convert('RGB')
                pil_img = pil_img.resize((size, size), resample_method)
            except Exception:
                pil_img = None
        if pil_img is None:
            try:
                path = os.path.join(self.folder_path, filename)
                pil_img = Image.open(path).convert('RGB')
                pil_img = pil_img.resize((size, size), resample_method)
            except Exception:
                pil_img = None
        if pil_img:
            self.tk_img = ImageTk.PhotoImage(pil_img)
            self.image_canvas.create_image(0, 0, anchor='nw', image=self.tk_img)
        else:
            self.image_canvas.create_text(size//2, size//2, text="Not Found", fill="white", font=("Helvetica",20))

        self.cell_size = max(1, size // 10)
        self.grid = []
        for i in range(10):
            for j in range(10):
                x1, y1 = j*self.cell_size, i*self.cell_size
                x2, y2 = x1+self.cell_size, y1+self.cell_size
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
        selected = self.selected_cells.get(filename, set())
        for idx in range(100):
            if idx in selected:
                self.image_canvas.itemconfig(self.grid[idx], fill='blue', stipple='gray25')
            else:
                self.image_canvas.itemconfig(self.grid[idx], fill='', stipple='')

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
        idx = row*10 + col
        filename = self.current_image_info['Filename']

        if single_click:
            if idx in self.selected_cells[filename]:
                self.selected_cells[filename].remove(idx)
            else:
                self.selected_cells[filename].add(idx)
            self.last_toggled_cell = idx
        else:
            if getattr(self, 'last_toggled_cell', None) == idx:
                return
            self.last_toggled_cell = idx
            if idx not in self.selected_cells[filename]:
                self.selected_cells[filename].add(idx)
            else:
                self.selected_cells[filename].discard(idx)
        self.update_grid_selection()

    def prev_land_image(self):
        if self.current_land_index > 0:
            self.save_land_cover()
            self.current_land_index -= 1
            self.load_land_image()
            self.next_land_button.config(state='normal')
        if self.current_land_index == 0:
            self.prev_land_button.config(state='disabled')

    def next_land_image(self):
        self.save_land_cover()
        if self.current_land_index < self.total_land - 1:
            self.current_land_index += 1
            self.load_land_image()
            self.prev_land_button.config(state='normal')
        else:
            self.next_land_button.config(state='disabled')

    def save_land_cover(self):
        filename = self.current_image_info['Filename']
        selected_count = len(self.selected_cells.get(filename, set()))
        percent_land = f"{(selected_count/100)*100:.2f}%"
        for img in self.results:
            if img['Filename'] == filename:
                img['Percent Land Cover'] = percent_land
                break

    def all_land(self):
        filename = self.current_image_info['Filename']
        self.selected_cells[filename] = set(range(100))
        self.update_grid_selection()

    def mark_water(self):
        filename = self.current_image_info['Filename']
        self.selected_cells[filename] = set()
        self.update_grid_selection()
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
                fieldnames = ['Filename','Classification','Confidence','Percent Land Cover','ThumbnailPath']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.results:
                    writer.writerow(row)
            messagebox.showinfo("Success", f"Validation complete!\nSaved: {self.csv_path}")
        except Exception as e:
            logging.error("Failed to write CSV", exc_info=True)
            messagebox.showerror("Error", f"Failed to write CSV.\n{e}")
        finally:
            self.validation_window.destroy()

# ------------------------- ENTRY POINT -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root, model_path='best_model.keras')
    root.mainloop()
