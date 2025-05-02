import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import pandas as pd
import piexif
import xml.etree.ElementTree as ET
import numpy as np

class ImageMetadataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Metadata Extractor and Cropper")

        # Variables
        self.folder_path = tk.StringVar()
        self.transect_file = tk.StringVar()
        self.final_metadata_csv = tk.StringVar()
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.output_csv = tk.StringVar()
        self.crop_pixel_size = tk.StringVar(value="125")
        self.kml_file = tk.StringVar()
        self.min_altitude = tk.StringVar(value="152")
        self.max_altitude = tk.StringVar(value="244")
        self.process_all = tk.BooleanVar(value=False)  # New checkbox

        self.create_widgets()

    def create_widgets(self):
        instr = (
            "5. Run Preprocessing\n"
            "a. For input folder: select your Images folder inside your MM_DD folder\n"
            "b. For the transect csv: select the transect assignment csv created in step 4\n"
            "c. (Optional) Select KML for GPS correction\n"
            "d. Run ‘Extract & Assign Transects’"
        )
        tk.Label(self.root, text=instr, justify="left").grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="Select Input Folder:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.folder_path, width=40).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_folder).grid(row=1, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Select Transect CSV:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.transect_file, width=40).grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_csv).grid(row=2, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Select KML File:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.kml_file, width=40).grid(row=3, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_kml).grid(row=3, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Crop Pixel Size:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.crop_pixel_size, width=10).grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Min Altitude (m):").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.min_altitude, width=10).grid(row=5, column=1, padx=10, pady=5)

        tk.Label(self.root, text="Max Altitude (m):").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.max_altitude, width=10).grid(row=6, column=1, padx=10, pady=5)

        # New checkbox to ignore filters
        tk.Checkbutton(
            self.root,
            text="Process All Images (ignore transect/altitude)",
            variable=self.process_all
        ).grid(row=7, column=0, columnspan=3, padx=10, pady=5)

        tk.Button(self.root, text="Convert KML to CSV", command=self.run_kml_to_csv_conversion).grid(row=8, column=0, columnspan=3, padx=10, pady=5)
        tk.Button(self.root, text="Extract & Assign Transects", command=self.run_extract_and_assign).grid(row=9, column=0, columnspan=3, padx=10, pady=5)
        tk.Button(self.root, text="Crop Images", command=self.run_crop_images).grid(row=10, column=0, columnspan=3, padx=10, pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def browse_csv(self):
        csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*transect_assignment.csv"), ("All Files", "*.*")])
        if csv_file:
            self.transect_file.set(csv_file)

    def browse_kml(self):
        kml_filepath = filedialog.askopenfilename(filetypes=[("KML Files", "*.kml"), ("All Files", "*.*")])
        if kml_filepath:
            self.kml_file.set(kml_filepath)

    def run_kml_to_csv_conversion(self):
        if not self.kml_file.get():
            messagebox.showerror("Error", "Please select a KML file.")
            return
        out_csv = os.path.splitext(self.kml_file.get())[0] + '.csv'
        self.kml_to_csv(self.kml_file.get(), out_csv)
        messagebox.showinfo("Success", "KML file converted to CSV successfully!")

    def run_extract_and_assign(self):
        if not self.folder_path.get() or not self.transect_file.get():
            messagebox.showerror("Error", "Please select both the input folder and the transect CSV.")
            return
        self.final_metadata_csv.set(os.path.join(self.folder_path.get(), 'final_metadata.csv'))
        self.output_folder.set(os.path.join(self.folder_path.get(), 'cropped_images_on_tx', 'Images'))
        self.output_csv.set(self.final_metadata_csv.get())

        self.extract_and_assign_transects(
            self.folder_path.get(),
            self.transect_file.get(),
            self.final_metadata_csv.get()
        )

        kml_csv = os.path.splitext(self.kml_file.get())[0] + '.csv'
        if os.path.exists(kml_csv):
            self.integrate_csv_data()
            messagebox.showinfo("Success", "Transects extracted, assigned, and integrated successfully!")
        else:
            messagebox.showinfo("Success", "Transects extracted and assigned successfully!")

    def run_crop_images(self):
        if not self.folder_path.get():
            messagebox.showerror("Error", "Please select the input folder first.")
            return

        meta_csv = self.final_metadata_csv.get()
        if not meta_csv or not os.path.exists(meta_csv):
            df = self.extract_metadata_from_folder(self.folder_path.get())
            meta_csv = os.path.join(self.folder_path.get(), 'metadata_only.csv')
            df.to_csv(meta_csv, index=False)

        self.input_folder.set(self.folder_path.get())
        self.output_folder.set(os.path.join(self.folder_path.get(), 'cropped_images'))
        self.crop_images_based_on_transect(
            meta_csv,
            self.input_folder.get(),
            self.output_folder.get(),
            crop_amount=int(self.crop_pixel_size.get()),
            ignore_filters=self.process_all.get()
        )
        messagebox.showinfo("Success", "Images cropped successfully!")

    # --- Core logic below unchanged except for new parameter in crop_images_based_on_transect ---

    def get_geotagging(self, exif):
        if not exif:
            return None
        geo = {}
        for idx, tag in TAGS.items():
            if tag == 'GPSInfo':
                if idx not in exif:
                    return None
                for key, val in GPSTAGS.items():
                    if key in exif[idx]:
                        geo[val] = exif[idx][key]
        return geo

    def dms_to_decimal(self, d, m, s, ref):
        dec = d + (m / 60.0) + (s / 3600.0)
        return -dec if ref in ['S', 'W'] else dec

    def extract_metadata_from_folder(self, folder_path):
        rows = []
        for root_, _, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    path = os.path.join(root_, f).replace('\\', '/')
                    try:
                        img = Image.open(path)
                        ex = img._getexif()
                    except:
                        ex = None
                    if not ex:
                        rows.append([path, 'NA', 'NA', 'NA', 'NA'])
                        continue
                    dt = ex.get(36867, 'NA')
                    geo = self.get_geotagging(ex)
                    if not geo:
                        rows.append([path, dt, 'NA', 'NA', 'NA'])
                        continue
                    alt = geo.get('GPSAltitude', 'NA')
                    lat = lon = 'NA'
                    if 'GPSLatitude' in geo and 'GPSLatitudeRef' in geo:
                        lat = self.dms_to_decimal(*geo['GPSLatitude'], geo['GPSLatitudeRef'])
                    if 'GPSLongitude' in geo and 'GPSLongitudeRef' in geo:
                        lon = self.dms_to_decimal(*geo['GPSLongitude'], geo['GPSLongitudeRef'])
                    rows.append([path, dt, lat, lon, alt])
        return pd.DataFrame(rows, columns=['Filepath', 'DatetimeOriginal', 'Latitude', 'Longitude', 'Altitude'])

    def extract_and_assign_transects(self, folder_path, transect_file, output_csv):
        df = pd.read_csv(transect_file)
        if 'start_img' in df and 'end_img' in df:
            df['start_img'] = df['start_img'].astype(str).str.replace('\\', '/', regex=False)
            df['end_img']   = df['end_img'].astype(str).str.replace('\\', '/', regex=False)
            df.to_csv(transect_file, index=False)

        ta = pd.read_csv(transect_file)
        md = self.extract_metadata_from_folder(folder_path)
        md['Transect'] = 'NA'

        for _, row in ta.iterrows():
            st = et = None
            if 'start_img' in row and 'end_img' in row and pd.notna(row['start_img']) and pd.notna(row['end_img']):
                s = md.loc[md['Filepath']==row['start_img'], 'DatetimeOriginal'].values
                e = md.loc[md['Filepath']==row['end_img'],   'DatetimeOriginal'].values
                if s.size and e.size:
                    st, et = s[0], e[0]
            if (st is None or et is None) and 'start_time' in row and 'end_time' in row:
                st, et = row['start_time'], row['end_time']
            if not (st and et):
                continue
            mask = (md['DatetimeOriginal'] >= str(st)) & (md['DatetimeOriginal'] <= str(et))
            md.loc[mask, 'Transect'] = row.get('transect_id', 'NA')

        md.to_csv(output_csv, index=False)
        return output_csv

    def kml_to_csv(self, kml_fp, csv_fp):
        tree = ET.parse(kml_fp)
        root_ = tree.getroot()
        ns = {'kml':'http://www.opengis.net/kml/2.2'}
        ns_ext = {'gx':'http://www.google.com/kml/ext/2.2'}
        coords, times = [], []
        for pm in root_.findall(".//kml:Placemark", ns):
            for c, w in zip(pm.findall(".//gx:coord", ns_ext), pm.findall(".//kml:when", ns)):
                coords.append(c.text.strip().split())
                times.append(w.text)
        df = pd.DataFrame(coords, columns=["Longitude","Latitude","Altitude"])
        df["Datetime"] = times
        df.to_csv(csv_fp, index=False)

    def integrate_csv_data(self):
        base = pd.read_csv(self.final_metadata_csv.get())
        kml_csv = os.path.splitext(self.kml_file.get())[0] + '.csv'
        if not os.path.exists(kml_csv):
            return
        a = base.copy()
        b = pd.read_csv(kml_csv)
        a['Datetime'] = pd.to_datetime(a['DatetimeOriginal'], format='%Y:%m:%d %H:%M:%S', errors='coerce')
        b['Datetime'] = pd.to_datetime(b['Datetime'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce')
        a['TS'] = a['Datetime'].apply(lambda x: x.timestamp() if not pd.isnull(x) else np.nan)
        b['TS'] = b['Datetime'].apply(lambda x: x.timestamp() if not pd.isnull(x) else np.nan)

        def closest(r):
            diffs = (b['TS'] - r['TS']).abs()
            idx = diffs.idxmin()
            return b.loc[idx, ['Latitude','Longitude','Altitude']] if diffs[idx] <= 3 else pd.Series([np.nan]*3, index=['Latitude','Longitude','Altitude'])

        cv = a.apply(closest, axis=1)
        a[['LatitudeNew','LongitudeNew','AltitudeNew']] = cv
        a.to_csv(os.path.splitext(self.final_metadata_csv.get())[0] + '_updated.csv', index=False)

    def crop_images_based_on_transect(self, final_metadata_csv, input_folder, output_folder, crop_amount=125, ignore_filters=False):
        import concurrent.futures

        def decimal_to_dms(decimal):
            d = int(decimal)
            m = int((decimal - d) * 60)
            s = (decimal - d - m/60) * 3600
            return ((d,1),(m,1),(int(s*1000),1000))

        upd_csv = os.path.join(os.path.dirname(final_metadata_csv), 'final_metadata_updated.csv')
        md = pd.read_csv(upd_csv) if os.path.exists(upd_csv) else pd.read_csv(final_metadata_csv)

        if not ignore_filters:
            if 'Transect' in md.columns:
                md = md[md['Transect'].notna() & (md['Transect']!='NA')]
            if 'Altitude' in md.columns:
                md['Altitude'] = pd.to_numeric(md['Altitude'], errors='coerce')
                md = md[(md['Altitude'] >= float(self.min_altitude.get())) & (md['Altitude'] <= float(self.max_altitude.get()))]

        valid_images = md.copy()

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # assign new filenames
        self.count0 = getattr(self, 'count0', 0)
        self.count1 = getattr(self, 'count1', 0)
        for idx, row in valid_images.iterrows():
            folder = os.path.basename(os.path.dirname(row['Filepath']))
            if folder == '0':
                self.count0 += 1
                num, pref = self.count0, '0'
            elif folder == '1':
                self.count1 += 1
                num, pref = self.count1, '1'
            else:
                valid_images.at[idx, 'NewFilename'] = None
                continue
            valid_images.at[idx, 'NewFilename'] = f"{pref}_000_00_{num:03d}.jpg"

        def process(idx, row):
            if not row['NewFilename'] or not os.path.exists(row['Filepath']):
                return idx, None
            img = Image.open(row['Filepath'])
            w, h = img.size
            crop_box = (crop_amount, crop_amount, w, h)
            crop = img.crop(crop_box)
            try:
                exif = piexif.load(img.info.get("exif", b""))
            except:
                exif = {"0th":{}, "Exif":{}, "GPS":{}, "Interop":{}, "1st":{}}

            if 'LatitudeNew' in row and not pd.isna(row['LatitudeNew']):
                gps = {
                    piexif.GPSIFD.GPSLatitudeRef: 'S' if row['LatitudeNew']<0 else 'N',
                    piexif.GPSIFD.GPSLatitude: decimal_to_dms(abs(row['LatitudeNew'])),
                    piexif.GPSIFD.GPSLongitudeRef:'W' if row['LongitudeNew']<0 else 'E',
                    piexif.GPSIFD.GPSLongitude:decimal_to_dms(abs(row['LongitudeNew'])),
                    piexif.GPSIFD.GPSAltitudeRef:0,
                    piexif.GPSIFD.GPSAltitude:(int(abs(row['AltitudeNew'])*1000),1000),
                }
                exif['GPS'] = gps

            outp = os.path.join(output_folder, row['NewFilename'])
            crop.save(outp, quality=100, exif=piexif.dump(exif))
            return idx, outp

        results = {}
        with concurrent.futures.ThreadPoolExecutor() as exe:
            futs = {exe.submit(process, i, r): i for i, r in valid_images.iterrows()}
            for fut in concurrent.futures.as_completed(futs):
                i, path = fut.result()
                if path:
                    results[i] = path

        for i, path in results.items():
            md.loc[i, 'NewFilepath'] = path

        md.to_csv(final_metadata_csv, index=False)
        md.to_csv(os.path.splitext(final_metadata_csv)[0] + '_updated_filepath.csv', index=False)
        print(f"Cropping done, saved in {output_folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMetadataGUI(root)
    root.mainloop()
