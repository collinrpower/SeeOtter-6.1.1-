import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import tensorflow as tf
import numpy as np
import csv
from datetime import datetime
import threading
import json
from pathlib import Path
import hashlib
import logging
import io
from tensorflow.keras import mixed_precision
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys
import webbrowser   # fallback for very old systems
from tensorflow.keras.losses import SparseCategoricalCrossentropy
import logging
logging.basicConfig(
    filename='app_log.txt',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)




def open_external(path: Path) -> None:
    """Open *path* with the OS default image viewer."""
    try:                           # Windows
        os.startfile(path)
    except AttributeError:
        try:                       # macOS
            subprocess.run(["open", path], check=False)
        except FileNotFoundError:  # Linux / BSD
            try:
                subprocess.run(["xdg-open", path], check=False)
            except FileNotFoundError:
                webbrowser.open(path.as_uri())   # last resort


def _decode_and_thumb(full_path: Path, thumb_max: int) -> tuple:
    """
    Worker used in the thread‑pool.

    Returns ( filename:str ,
              sha256:str ,
              cnn_input: np.ndarray | None ,
              err_msg: str | None )
    """
    fn = full_path.name
    try:
        # ---- one disk read -------------------------------------------------
        with open(full_path, "rb") as fh:
            raw = fh.read()

        sha = hashlib.sha256(raw).hexdigest()

        # ---- fast decode with draft() --------------------------------------
        with Image.open(io.BytesIO(raw)) as im:
            im.draft("RGB", (thumb_max, thumb_max))   # <= 1/8 original size
            im = im.convert("RGB")

            # ① save the thumbnail if missing
            thumb_dir   = full_path.parent / THUMB_DIR
            thumb_dir.mkdir(exist_ok=True)
            thumb_file  = thumb_dir / fn
            if not thumb_file.exists():
                tmp = im.copy()
                tmp.thumbnail((thumb_max, thumb_max), Image.LANCZOS)
                tmp.save(thumb_file, "JPEG", quality=85, optimize=True)

            # ② 128 px array for the CNN
            cnn_img = im.resize(IMG_SIZE, Image.LANCZOS)
            cnn_arr = np.asarray(cnn_img, dtype=np.float32) / 255.0

        return fn, sha, cnn_arr, None

    except Exception as e:
        return fn, "N/A", None, str(e)

mixed_precision.set_global_policy("mixed_float16")


# use 1×CPU‑core per 4 logical cores for hashing
_SHA_POOL = ThreadPoolExecutor(max_workers=os.cpu_count()//4 or 1)

THUMB_DIR   = "thumbnails"   # sub‑folder name
THUMB_MAX   = 512            # longest side in px that we keep on disk

# --------------------------- CONSTANTS ---------------------------
class_names = ['Land', 'Water']
IMG_SIZE = (128, 128)          # size expected by the model
PH1_PER_PAGE = 14              # 3 rows × 7 columns
GRID_DIVISIONS = 10            # 10×10 grid for land‑cover selection

# --------------------------------------------------------------
#  CONSTANTS & GLOBAL HELPERS
# --------------------------------------------------------------
class_names = ["Land", "Water"]
IMG_SIZE    = (128, 128)          # model input
GRID_DIVS   = 10                  # 10×10 land‑cover grid

# --------------------------------------------------------------
#  DISPLAY‑AWARE SIZING HELPERS
# --------------------------------------------------------------

def get_screen_scale(master: tk.Tk):
    """Return a scaling factor: 1.0 on 1920×1080, >1 on HiDPI, <1 on low‑res."""
    base_w, base_h = 1920, 1080
    sw, sh = master.winfo_screenwidth(), master.winfo_screenheight()
    return min(sw / base_w, sh / base_h)


def thumb_geometry(scale):
    """Rows, Cols, Thumb‑Px per Phase‑1 page based on scale."""
    # keep aspect row≈col≈sqrt(n). use 14 thumbs @scale=1, more on big screens
    base_n = 14
    n = int(base_n * (0.5 + scale))
    cols = 7 if scale < 1.2 else 8 if scale < 1.6 else 9
    rows = max(1, n // cols)
    thumb = int(180 * scale)           # ~180 px @1×
    return rows, cols, thumb, rows*cols

# --------------------------------------------------------------
#  IMAGE PRE‑PROCESSING
# --------------------------------------------------------------
from functools import lru_cache

def ensure_thumbnail(src_path: Path) -> Path:
    """
    Make a <= THUMB_MAX px JPEG copy of *src_path* inside the THUMB_DIR
    sibling folder (created on demand) and return its path.
    If the thumb is already there, nothing is done.
    """
    thumb_dir  = src_path.parent / THUMB_DIR
    thumb_dir.mkdir(exist_ok=True)

    thumb_path = thumb_dir / src_path.name
    if thumb_path.exists():
        return thumb_path

    with Image.open(src_path) as im:
        im.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
        # always save as JPEG for huge space savings
        im.convert("RGB").save(thumb_path, "JPEG", quality=85, optimize=True)
    return thumb_path


@lru_cache(maxsize=2048)          # re‑use across pages
def get_thumb(path: Path, target: int) -> ImageTk.PhotoImage:
    """
    Load *path* (already a small jpeg) and resize to *target* px
    for current slider setting.  Result is cached in RAM.
    """
    try:
        with Image.open(path) as im:
            if max(im.size) != target:                       # cheap resize
                im = im.copy()
                im.thumbnail((target, target), Image.LANCZOS)
            return ImageTk.PhotoImage(im)
    except Exception as e:
        logging.warning("Thumb load failed: %s – %s", path, e)
        return None

def preprocess_image(path, target_size=IMG_SIZE):
    try:
        img = Image.open(path).convert("RGB").resize(target_size)
        return np.asarray(img, dtype=np.float32) / 255.0
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}")
        return None

def decode_and_resize_tf(path: tf.Tensor) -> tf.Tensor:
    """read‑file → RGB → 128×128 float32 in [0,1]."""
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)              # or decode_png
    img = tf.image.resize(img, IMG_SIZE, method='area')
    return img / 255.0
# --------------------------------------------------------------
#  MAIN APPLICATION
# --------------------------------------------------------------
class MainApplication:

    def __init__(self, master: tk.Tk):
        if Path('last_session.json').exists():
            self.recover_path = 'last_session.json'
        else:
            self.recover_path = None
        self.master = master
        self.scale  = get_screen_scale(master)

        master.title("Land vs Water Image Classifier")
        w, h = int(600*self.scale), int(300*self.scale)
        master.geometry(f"{w}x{h}")
        master.resizable(False, False)

        # model load ------------------------------------------------

        try:
            # ---- load the saved weights but DON'T restore its old compile cfg ----
            model_path = Path(__file__).parent / "best_model.keras"
            self.model = tf.keras.models.load_model(model_path, compile=False)

            # ---- re‑compile with a TF‑2 loss object to silence the warning --------
            self.model.compile(
                optimizer="adam",
                #   if your model outputs **raw logits**       →  from_logits=True
                #   if your model ends with a soft‑max layer   →  from_logits=False
                loss=SparseCategoricalCrossentropy(from_logits=True),
                metrics=["accuracy"],
            )

        except Exception as e:
            logging.exception("Model load failed")
            messagebox.showerror("Model load failed", "Check app_log.txt for details")
            master.destroy()

        # UI --------------------------------------------------------
        pad = int(20*self.scale)
        frame = tk.Frame(master, padx=pad, pady=pad)
        frame.pack(expand=True, fill="both")

        font_big  = ("Helvetica", int(14*self.scale))
        font_btn  = ("Helvetica", int(12*self.scale))

        tk.Label(frame, text="Upload a folder of images to classify as Land or Water.", font=font_big).pack(pady=(0,pad))
        self.upload_btn = tk.Button(frame, text="Upload Folder", width=20, height=2, bg="blue", fg="white", font=font_btn, command=self.upload_folder)
        self.upload_btn.pack(pady=(0, pad))

        self.pbar = ttk.Progressbar(frame, length=int(400*self.scale))
        self.pbar.pack(pady=(0, pad//2))
        self.pbar_lbl = tk.Label(frame, font=font_btn)
        self.pbar_lbl.pack()

    # -------------------  folder select  -------------------
    def upload_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Images")
        if not folder: return
        images = [f for f in os.listdir(folder) if f.lower().endswith((".jpg",".jpeg",".png",".bmp",".gif"))]
        if not images:
            messagebox.showinfo("No Images", "No supported image files found."); return
        csv_out = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"classifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", filetypes=[("CSV", "*.csv")])
        if not csv_out: return

        self.upload_btn.config(state="disabled")
        self.pbar.configure(maximum=len(images), value=0)
        self.pbar_lbl.config(text="Starting …")
        # clear previous crash marker
        if Path('last_session.json').exists():
            Path('last_session.json').unlink()

        threading.Thread(target=self.process_images, args=(folder, images, csv_out), daemon=True).start()

    # -------------------  inference loop  ------------------
    def process_images(self, folder, images, csv_out, batch_size=64):
        """
        Now uses a thread‑pool so JPEG decode happens in parallel.
        """
        results = []
        keep_fns, keep_sha, cnn_arrays = [], [], []

        # ---------- threaded ingest --------------------------------------------
        max_workers = min(32, os.cpu_count() * 4)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_decode_and_thumb, Path(folder) / fn, THUMB_MAX)
                       : fn for fn in images}

            processed = 0
            total = len(images)

            for fut in as_completed(futures):
                fn, sha, arr, err = fut.result()

                if arr is not None:  # success
                    keep_fns.append(fn)
                    keep_sha.append(sha)
                    cnn_arrays.append(arr)
                else:  # error placeholder
                    results.append({
                        "Filename": fn,
                        "SHA256": sha,
                        "AI Classification": "Error",
                        "Classification": "Error",
                        "Confidence": "N/A",
                        "Percent Land Cover": "N/A"
                    })

                if err:
                    logging.warning("Decode error %s : %s", fn, err)

                processed += 1
                # update UI every single image
                self.master.after(
                    0,
                    lambda p=processed: (
                        self.pbar.configure(value=p),
                        self.pbar_lbl.config(text=f"Pre‑processing {p}/{total}")
                    )
                )

        # ---------- CNN inference ----------------------------------------------
        if cnn_arrays:
            arr_buf = np.asarray(cnn_arrays, dtype=np.float32)
            ds = (tf.data.Dataset.from_tensor_slices(arr_buf)
                  .batch(batch_size)
                  .prefetch(tf.data.AUTOTUNE))

            preds = self.model.predict(ds, verbose=0)

            if preds.ndim == 2 and preds.shape[1] == 2:  # ← ONLY real soft‑max
                lbl = np.argmax(preds, 1)
                conf = preds[np.arange(len(lbl)), lbl]
            else:  # ← sigmoid or (N,1)
                probs = preds.reshape(-1)  # (N,)
                lbl = (probs > 0.5).astype(int)
                conf = probs


            for fn, sha, lab, cf in zip(keep_fns, keep_sha, lbl, conf):
                results.append({
                    "Filename": fn,
                    "SHA256": sha,
                    "AI Classification": class_names[int(lab)],
                    "Classification": class_names[int(lab)],
                    "Confidence": f"{cf * 100:.2f}%",
                    "Percent Land Cover": "N/A"
                })

        # ---------- hand over to the GUI ---------------------------------------
        self.master.after(
            0,
            lambda: ValidationWindow(self.master, results, csv_out, folder, self.scale)
        )
        self.master.after(
            0,
            lambda: [self.upload_btn.config(state="normal"),
                     self.pbar_lbl.config(text="Processing complete."),
                     self.pbar.configure(value=len(images))]
        )


def thumb_path(src: Path, size: int) -> Path:
    d = Path("thumbs"); d.mkdir(exist_ok=True)
    return d / f"{src.stem}_{size}.jpg"


# --------------------- VALIDATION WINDOW ---------------------
class ValidationWindow:
    def __init__(self, master, results, csv_path, folder_path, scale):
        self.master = master
        self.results = results
        self.csv_path = csv_path
        self.folder_path = folder_path
        self.scale = scale
        self.rows, self.cols, self.thumb_px, _ = thumb_geometry(self.scale)
        self.thumb_cache = {}
        self.thumb_dir = Path(folder_path) / THUMB_DIR

        self.save_file = Path(csv_path).with_suffix('.json')
        self.selected_cells = {}
        self.misclassified_water = []
        self.current_phase = 1
        self.water_page = 0
        self.current_land_index = 0

        # split results
        self.water_images = [r for r in self.results if r['Classification']=='Water']
        self.water_images.sort(key=lambda x: float(x['Confidence'].rstrip('%')) if x['Confidence']!='N/A' else 0, reverse=True)
        self.land_images = [r for r in self.results if r['Classification']=='Land']
        self.total_water_pages = max((len(self.water_images)-1)//PH1_PER_PAGE+1, 1)
        self.final_land_images = []   # filled after Phase1

        if self.save_file.exists() and messagebox.askyesno('Resume?', 'Load previous validation progress?'):
            self.load_progress()

        self.win = tk.Toplevel(master)
        self.win.title('Validation')
        self.win.geometry('1400x1100')
        self.win.grab_set()

        self.phase1_frame = tk.Frame(self.win)
        self.phase2_frame = tk.Frame(self.win)
        self.setup_phase1() if self.current_phase==1 else self.setup_phase2()

        self.autosave_interval_ms = 30_000
        self.win.after(self.autosave_interval_ms, self.autosave_tick)

    def autosave_tick(self):
        try:
            self.save_progress()
        except Exception as e:
            logging.exception("Autosave failed: %s", e)
        finally:
            self.win.after(self.autosave_interval_ms, self.autosave_tick)

    # --------------------- PHASE 1 (WATER) ---------------------
    def setup_phase1(self):
        self.current_phase = 1
        self.phase2_frame.pack_forget()
        self.phase1_frame.pack(fill='both', expand=True)
        tk.Label(self.phase1_frame, text='Phase 1: Validate Water Images', font=('Helvetica',16)).pack(pady=10)

        self.water_page_lbl = tk.Label(self.phase1_frame, font=('Helvetica',12))
        self.water_page_lbl.pack(pady=5)

        self.size_scale = tk.Scale(self.phase1_frame, from_=50, to=300, orient='horizontal', label='Image Size (px)'); self.size_scale.set(200); self.size_scale.pack(pady=5)

        c_container = tk.Frame(self.phase1_frame, height=700); c_container.pack(fill='x', padx=10, pady=5); c_container.pack_propagate(False)
        self.canvas = tk.Canvas(c_container, bg='white'); vsb = tk.Scrollbar(c_container, orient='vertical', command=self.canvas.yview)
        vsb.pack(side='right', fill='y'); self.canvas.configure(yscrollcommand=vsb.set); self.canvas.pack(side='left', fill='both', expand=True)
        self.grid_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0,0), window=self.grid_frame, anchor='nw')
        self.grid_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        nav = tk.Frame(self.phase1_frame); nav.pack(pady=10)
        self.prev_btn = tk.Button(nav, text='Previous', command=self.prev_water_page); self.prev_btn.grid(row=0, column=0, padx=10)
        self.next_btn = tk.Button(nav, text='Next', command=self.next_water_page); self.next_btn.grid(row=0, column=1, padx=10)
        tk.Button(self.phase1_frame, text='Save Progress', command=self.save_progress).pack(pady=5)

        self.load_water_page(); self.update_water_nav()

    def load_water_page(self) -> None:
        """Populate the Phase‑1 (water) grid with thumbnails + radio buttons."""
        # ── 1. clear old widgets ──────────────────────────────────────────────
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.radio_vars = []

        start = self.water_page * PH1_PER_PAGE
        current = self.water_images[start: start + PH1_PER_PAGE]

        rows, cols = self.rows, self.cols
        size = self.size_scale.get()

        for idx, info in enumerate(current):
            r, c = divmod(idx, cols)
            cell = tk.Frame(self.grid_frame, bg="white", bd=2,
                            relief="groove", padx=5, pady=5)
            cell.grid(row=r, column=c, padx=5, pady=5)

            # ── 2. thumbnail lookup ───────────────────────────────────────────
            thumb_file = (self.thumb_dir / info["Filename"])
            if not thumb_file.exists():
                # fallback to original image if thumb hasn’t been created yet
                thumb_file = Path(self.folder_path) / info["Filename"]

            imtk = None
            try:
                imtk = get_thumb(thumb_file, size)  # your cached helper
            except Exception as e:
                logging.warning("Thumb error %s : %s", thumb_file, e)

            if imtk is None:
                tk.Label(cell, text="Not Found", width=20, height=10,
                         bg="grey").pack()
            else:
                lbl = tk.Label(cell, image=imtk)
                lbl.image = imtk  # <‑‑ hold a reference!
                lbl.pack()

            # ── 3. radio buttons  (Water / Land / Exclude) ────────────────────
            status = info["Classification"]
            default = 0 if status == "Water" else 1 if status == "Land" else 2
            var = tk.IntVar(value=default)
            self.radio_vars.append(var)

            for txt, val in (("Water", 0), ("Land", 1), ("Exclude", 2)):
                tk.Radiobutton(cell, text=txt, variable=var, value=val,
                               bg="white").pack(anchor="w")

            # ── 4. filename + confidence text ─────────────────────────────────
            # ---------- filename + confidence (click‑to‑open) ----------
            fname_label = tk.Label(
                cell,
                text=f"{info['Filename']}\nConf: {info['Confidence']}",
                font=("Helvetica", 10, "underline"),  # underline = looks like a link
                fg="blue",
                bg="white",
                cursor="hand2"
            )
            fname_label.pack()

            # keep a Path now so it works no matter if the thumb exists or not
            full_img = Path(self.folder_path) / info["Filename"]

            # left‑click opens the file
            fname_label.bind(
                "<Button-1>",
                lambda e, p=full_img: open_external(p)
            )

        # ── 5. page indicator ────────────────────────────────────────────────
        self.water_page_lbl.config(
            text=f"Page {self.water_page + 1} / {self.total_water_pages}"
        )

    def save_water_misclassifications(self):
        start = self.water_page*PH1_PER_PAGE; end = start+PH1_PER_PAGE
        for idx, img_info in enumerate(self.water_images[start:end]):
            choice = self.radio_vars[idx].get()

            if choice == 0:  # keep as Water
                img_info['Classification'] = 'Water'
                if img_info in self.misclassified_water:
                    self.misclassified_water.remove(img_info)

            elif choice == 1:  # mark as Land
                img_info['Classification'] = 'Land'
                if img_info not in self.misclassified_water:
                    self.misclassified_water.append(img_info)

            else:  # choice == 2 → Exclude
                img_info['Classification'] = 'Excluded'
                if img_info in self.misclassified_water:
                    self.misclassified_water.remove(img_info)
        self.total_water_pages = max((len(self.water_images) - 1) // PH1_PER_PAGE + 1, 1)

    def prev_water_page(self):
        self.water_images.sort(key=lambda x: float(x['Confidence'].rstrip('%')) if x['Confidence'] != 'N/A' else 0,
                               reverse=True)
        if self.water_page==0: return
        self.save_water_misclassifications(); self.water_page-=1; self.save_progress(); self.thumb_cache.clear(); self.load_water_page(); self.update_water_nav()

    def next_water_page(self):
        self.water_images.sort(key=lambda x: float(x['Confidence'].rstrip('%')) if x['Confidence'] != 'N/A' else 0,
                               reverse=True)
        self.save_water_misclassifications(); self.save_progress()
        if self.water_page < self.total_water_pages-1:
            self.water_page+=1; self.thumb_cache.clear(); self.load_water_page(); self.update_water_nav()
        else:
            self.phase1_to_phase2()

    def update_water_nav(self):
        self.prev_btn.config(state='normal' if self.water_page>0 else 'disabled')
        self.next_btn.config(text='Proceed' if self.water_page>=self.total_water_pages-1 else 'Next')

    # -------------------- PHASE TRANSITION -------------------
    def phase1_to_phase2(self) -> None:
        """
        Finish Phase‑1, show a summary, then switch to Phase‑2.
        """
        # ------------------------------------------------------------------
        # 1)  Calculate how many water thumbnails were changed in Phase‑1
        # ------------------------------------------------------------------
        reclassified = sum(img["Classification"] == "Land" for img in self.water_images)
        excluded = sum(img["Classification"] == "Excluded" for img in self.water_images)

        # ------------------------------------------------------------------
        # 2)  Inform the user
        # ------------------------------------------------------------------
        msg = (f"Phase 1 complete!\n\n"
               f"• Re‑classified as **Land** : {reclassified}\n"
               f"• Marked **Excluded**       : {excluded}\n\n"
               f"Click **OK** to continue to Phase 2.")
        messagebox.showinfo("Water‑validation summary", msg, parent=self.win)

        # ------------------------------------------------------------------
        # 3)  Build the Phase‑2 list and switch UI
        # ------------------------------------------------------------------
        self.final_land_images = self.land_images + self.misclassified_water
        self.phase1_frame.pack_forget()
        self.setup_phase2()
    # --------------------- PHASE 2 (LAND) ---------------------
    def setup_phase2(self):
        self.current_phase = 2
        self.phase1_frame.pack_forget()
        self.phase2_frame.pack(fill='both', expand=True)
        tk.Label(self.phase2_frame, text='Phase 2: Validate Land Images', font=('Helvetica',16)).pack(pady=10)

        self.land_idx_lbl = tk.Label(self.phase2_frame, font=('Helvetica',12)); self.land_idx_lbl.pack(pady=5)
        self.size2 = tk.Scale(self.phase2_frame, from_=100, to=900, orient='horizontal', label='Display Size (px)'); self.size2.set(600); self.size2.pack(pady=5)

        self.canvas = tk.Canvas(self.phase2_frame, width=600, height=600, bg='grey'); self.canvas.pack(pady=10)
        btnf = tk.Frame(self.phase2_frame); btnf.pack(pady=5)
        tk.Button(btnf, text='All Land', command=self.all_land).grid(row=0,column=0,padx=5)
        tk.Button(btnf, text='Water', command=self.mark_water).grid(row=0,column=1,padx=5)
        tk.Button(btnf, text='Exclude', command=self.exclude_image).grid(row=0,column=2,padx=5)

        nav = tk.Frame(self.phase2_frame); nav.pack(pady=10)
        self.prev_land_btn = tk.Button(nav, text='Previous', command=self.prev_land)
        self.prev_land_btn.grid(row=0,column=0,padx=10)
        self.next_land_btn = tk.Button(nav, text='Next', command=self.next_land)
        self.next_land_btn.grid(row=0,column=1,padx=10)

        tk.Button(self.phase2_frame, text='Save Progress', command=self.save_progress).pack(pady=5)
        tk.Button(self.phase2_frame, text='Generate CSV', bg='green', fg='white', font=('Helvetica',12), command=self.generate_csv).pack(pady=10)

        self.load_land(); self.update_land_nav()

    # ---------------- LAND IMAGE HANDLING ------------------
    def load_land(self):
        if not (0 <= self.current_land_index < len(self.final_land_images)):
            return

        # clear the canvas
        self.canvas.delete('all')

        info = self.final_land_images[self.current_land_index]  # <‑‑ the one image
        fname = info['Filename']  # handy alias
        size = self.size2.get()

        # ------------------------------------------------------------------
        try:
            imtk = ImageTk.PhotoImage(
                Image.open(Path(self.folder_path) / fname)
                    .convert('RGB')
                    .resize((size, size))
            )
            self.canvas.create_image(0, 0, anchor='nw', image=imtk)
            self.canvas.image = imtk  # keep reference!
        except Exception:
            self.canvas.create_text(
                size // 2, size // 2,
                text='Not Found', fill='white', font=('Helvetica', 20)
            )

        # ---------- 10×10 overlay grid ------------------------------------
        cell = size // GRID_DIVISIONS
        self.grid_ids = []
        for r in range(GRID_DIVISIONS):
            for c in range(GRID_DIVISIONS):
                x1, y1 = c * cell, r * cell
                rid = self.canvas.create_rectangle(
                    x1, y1, x1 + cell, y1 + cell,
                    outline='white', tags='grid'
                )
                self.grid_ids.append(rid)

        # make sure an entry exists in selected_cells
        self.selected_cells.setdefault(fname, set())
        self.update_grid_fill()

        # mouse bindings
        self.canvas.bind('<Button-1>', self.click_grid)
        self.canvas.bind('<B1-Motion>', self.drag_grid)

        # status label
        self.land_idx_lbl.config(
            text=f"Image {self.current_land_index + 1} / {len(self.final_land_images)}"
        )

    def update_grid_fill(self) -> None:
        sel = self.selected_cells[self.final_land_images[self.current_land_index]['Filename']]

        for i, rid in enumerate(self.grid_ids):
            if i in sel:  # selected  →  blue, 50 % transparent
                self.canvas.itemconfig(
                    rid,
                    fill="red",  # any colour you like
                    stipple="gray12"  # ‘gray12’, ‘gray25’, ‘gray50’, ‘gray75’
                )
            else:  # not selected  →  fully transparent
                self.canvas.itemconfig(
                    rid,
                    fill="",  # no fill
                    stipple=""  # remove previous stipple
                )

    def grid_index(self, event):
        size = self.size2.get(); cell = size//GRID_DIVISIONS
        col, row = event.x//cell, event.y//cell
        if col>=GRID_DIVISIONS or row>=GRID_DIVISIONS: return None
        return row*GRID_DIVISIONS+col

    def click_grid(self, e):
        idx = self.grid_index(e);
        if idx is None: return
        fname = self.final_land_images[self.current_land_index]['Filename']
        sel = self.selected_cells[fname]
        if idx in sel: sel.remove(idx); self.selecting=False
        else: sel.add(idx); self.selecting=True
        self.last_idx = idx
        self.update_grid_fill()

    def drag_grid(self, e):
        idx = self.grid_index(e);
        if idx is None or idx==getattr(self,'last_idx',None): return
        fname = self.final_land_images[self.current_land_index]['Filename']
        sel = self.selected_cells[fname]
        if self.selecting: sel.add(idx)
        else: sel.discard(idx)
        self.last_idx = idx
        self.update_grid_fill()

    # ------------ NAVIGATION & QUICK ACTIONS -------------
    def prev_land(self):
        if self.current_land_index==0: return
        self.save_land_cover(); self.current_land_index-=1; self.save_progress(); self.load_land(); self.update_land_nav()

    def next_land(self):
        self.save_land_cover(); self.save_progress()
        if self.current_land_index < len(self.final_land_images)-1:
            self.current_land_index+=1; self.load_land(); self.update_land_nav()
        else:
            self.next_land_btn.config(state='disabled')

    def update_land_nav(self):
        self.prev_land_btn.config(state='normal' if self.current_land_index>0 else 'disabled')
        self.next_land_btn.config(state='normal' if self.current_land_index < len(self.final_land_images)-1 else 'disabled')

    def all_land(self):
        fname = self.final_land_images[self.current_land_index]['Filename']
        self.selected_cells[fname] = set(range(GRID_DIVISIONS*GRID_DIVISIONS))
        self.update_grid_fill()

    def mark_water(self):
        fname = self.final_land_images[self.current_land_index]['Filename']
        self.selected_cells[fname] = set()
        self.update_grid_fill()
        for r in self.results:
            if r['Filename']==fname:
                r['Classification']='Water'; r['Percent Land Cover']='N/A'
                break

    def exclude_image(self):
        fname = self.final_land_images[self.current_land_index]['Filename']
        for r in self.results:
            if r['Filename']==fname:
                r['Classification']='Excluded'; r['Percent Land Cover']='N/A'
                break
        self.next_land()

    # --------------------- DATA SAVING --------------------
    def save_land_cover(self):
        fname = self.final_land_images[self.current_land_index]['Filename']
        # guarantee the entry exists
        sel = self.selected_cells.setdefault(fname, set())

        # convert selected‑cell count to percentage (or keep it simple if you wish)
        percent = f"{len(sel)}%"

        for rec in self.results:
            if rec['Filename'] == fname:
                rec['Percent Land Cover'] = percent if sel else 'N/A'
                break

    def save_progress(self):

        state = {
            'results': self.results,
            'current_phase': self.current_phase,
            'water_page': self.water_page,
            'misclassified_water': self.misclassified_water,
            'selected_cells': {k:list(v) for k,v in self.selected_cells.items()},
            'current_land_index': self.current_land_index
        }
        try:
            with open(self.save_file, 'w') as f:
                json.dump(state, f)
            # keep a global backup
            with open('last_session.json', 'w') as f:
                json.dump({'csv': self.csv_path}, f)
        except Exception as e:
            messagebox.showerror('Save Error', str(e))

    # ------------------------- LOAD PROGRESS ------------------------
    def load_progress(self):
        try:
            with open(self.save_file) as f:
                state = json.load(f)
            # basic key‑checks
            for k in ("results", "current_phase", "water_page",
                       "misclassified_water", "selected_cells",
                       "current_land_index"):
                if k not in state:
                    raise KeyError(f"Missing {k}")
            self.results              = state["results"]
            self.current_phase        = state["current_phase"]
            self.water_page           = state["water_page"]
            self.misclassified_water  = state["misclassified_water"]
            self.selected_cells       = {k: set(v) for k, v in state["selected_cells"].items()}
            self.current_land_index   = state["current_land_index"]

            # rebuild derived lists & bounds‑check
            self.final_land_images = []
            self.rebuild_lists()
            self.water_page        = min(self.water_page, self.total_water_pages-1)
            self.current_land_index = min(self.current_land_index,
                                          max(len(self.final_land_images)-1, 0))
        except Exception as e:
            messagebox.showwarning("Load Error",
                                   f"Could not restore saved progress:\n{e}\nStarting fresh.")
            self.current_phase = 1
            self.water_page = self.current_land_index = 0
            self.misclassified_water.clear()
            self.selected_cells.clear()

    # ------------------------- CSV OUTPUT --------------------------
    # ──────────────────────────────────────────────────────────────
    #  ValidationWindow  ▶  generate_csv
    # ──────────────────────────────────────────────────────────────
    def generate_csv(self):
        # make sure the last image you're on is saved
        if self.current_phase == 2:
            self.save_land_cover()

        try:
            fieldnames = [
                "Filename",
                "SHA256",
                "AI Classification",  # ← new column
                "Classification",  # ← user‑editable column
                "Confidence",
                "Percent Land Cover"
            ]

            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    extrasaction="ignore"  # silently drop unknown keys
                )
                writer.writeheader()
                writer.writerows(self.results)

            self.save_progress()  # final autosave
            messagebox.showinfo(
                "Done",
                f"Validation complete!\nCSV saved to:\n{self.csv_path}"
            )
            self.win.destroy()

        except Exception as e:
            messagebox.showerror("Write Error", f"Failed to save CSV:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Percent Cover Land")

    try:
        app = MainApplication(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Initialization Error", f"Failed to start the application:\n{e}")
        root.destroy()
