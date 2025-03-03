import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import pandas as pd
import piexif
import xml.etree.ElementTree as ET
import numpy as np


import sys
print("sys.path:", sys.path)

class ImageMetadataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Metadata Extractor and Cropper")

        # Variables for file/folder paths, crop size, KML, etc.
        self.folder_path = tk.StringVar()
        self.transect_file = tk.StringVar()
        self.final_metadata_csv = tk.StringVar()
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.output_csv = tk.StringVar()
        self.crop_pixel_size = tk.StringVar()
        self.kml_file = tk.StringVar()

        # Defaults
        self.crop_pixel_size.set("125")
        self.min_altitude = tk.StringVar(value="152")
        self.max_altitude = tk.StringVar(value="244")

        self.create_widgets()

    def create_widgets(self):
        instruction_text = (
            "5. Run Preprocessing\n"
            "a. For input folder: select your Images folder inside your MM_DD folder\n"
            "b. For the transect csv: select the transect assignment csv created in step 4\n"
            "c. (Optional) Select KML for GPS correction\n"
            "d. Run ‘Extract & Assign Transects’"
        )
        tk.Label(self.root, text=instruction_text, justify="left").grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        tk.Label(self.root, text="Select Input Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.folder_path, width=40).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_folder).grid(row=1, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Select Transect CSV:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.transect_file, width=40).grid(row=2, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_csv).grid(row=2, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Select KML File:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.kml_file, width=40).grid(row=3, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_kml).grid(row=3, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Crop Pixel Size:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.crop_pixel_size, width=10).grid(row=4, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Min Altitude (m):").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.min_altitude, width=10).grid(row=5, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Max Altitude (m):").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(self.root, textvariable=self.max_altitude, width=10).grid(row=6, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Convert KML to CSV", command=self.run_kml_to_csv_conversion).grid(row=7, column=0,
                                                                                                     columnspan=3,
                                                                                                     padx=10, pady=10)
        tk.Button(self.root, text="Extract & Assign Transects", command=self.run_extract_and_assign).grid(row=8,
                                                                                                          column=0,
                                                                                                          columnspan=3,
                                                                                                          padx=10,
                                                                                                          pady=10)
        tk.Button(self.root, text="Crop Images", command=self.run_crop_images).grid(row=9, column=0, columnspan=3,
                                                                                    padx=10, pady=10)

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
        self.kml_to_csv(self.kml_file.get(), os.path.splitext(self.kml_file.get())[0] + '.csv')
        messagebox.showinfo("Success", "KML file converted to CSV successfully!")

    def run_extract_and_assign(self):
        if not self.folder_path.get() or not self.transect_file.get():
            messagebox.showerror("Error", "Please select both the input folder and the transect CSV.")
            return

        # Set final metadata CSV and output folder
        self.final_metadata_csv.set(os.path.join(self.folder_path.get(), 'final_metadata.csv'))
        self.output_folder.set(os.path.join(self.folder_path.get(), 'cropped_images_on_tx', 'Images'))
        self.output_csv.set(os.path.join(self.folder_path.get(), 'final_metadata.csv'))

        # Perform assignment
        self.extract_and_assign_transects(self.folder_path.get(),
                                          self.transect_file.get(),
                                          self.final_metadata_csv.get())

        # If there's a KML CSV, integrate
        if os.path.exists(os.path.splitext(self.kml_file.get())[0] + '.csv'):
            self.integrate_csv_data()
            messagebox.showinfo("Success", "Transects extracted, assigned, and integrated successfully!")
        else:
            messagebox.showinfo("Success", "Transects extracted and assigned successfully!")

    def run_crop_images(self):
        if not self.final_metadata_csv.get() or not self.folder_path.get() or not self.output_folder.get():
            messagebox.showerror("Error", "Please run 'Extract & Assign Transects' first.")
            return

        self.input_folder.set(self.folder_path.get())
        self.crop_images_based_on_transect(self.final_metadata_csv.get(),
                                           self.input_folder.get(),
                                           self.output_folder.get(),
                                           crop_amount=int(self.crop_pixel_size.get()))
        messagebox.showinfo("Success", "Images cropped successfully!")

    # -------------------------------
    # Core logic functions
    # -------------------------------
    def get_geotagging(self, exif):
        if not exif:
            return None
        geotagging = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                if idx not in exif:
                    return None
                for (key, val) in GPSTAGS.items():
                    if key in exif[idx]:
                        geotagging[val] = exif[idx][key]
        return geotagging

    def dms_to_decimal(self, degrees, minutes, seconds, ref):
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal

    def extract_metadata_from_folder(self, folder_path):
        data = []
        for root_, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(root_, file).replace('\\', '/')
                    try:
                        img = Image.open(img_path)
                        exif_data = img._getexif()
                    except:
                        exif_data = None

                    if not exif_data:
                        data.append([img_path, 'NA', 'NA', 'NA', 'NA'])
                        continue

                    datetime_original = exif_data.get(36867, 'NA')
                    geotags = self.get_geotagging(exif_data)

                    if not geotags:
                        data.append([img_path, datetime_original, 'NA', 'NA', 'NA'])
                        continue

                    # You could parse altitude here if it's a tuple
                    altitude = geotags.get('GPSAltitude', 'NA')
                    latitude = 'NA'
                    longitude = 'NA'
                    if 'GPSLatitude' in geotags and 'GPSLatitudeRef' in geotags:
                        lat_tuple = geotags['GPSLatitude']
                        lat_ref = geotags['GPSLatitudeRef']
                        latitude = self.dms_to_decimal(*lat_tuple, lat_ref)
                    if 'GPSLongitude' in geotags and 'GPSLongitudeRef' in geotags:
                        lon_tuple = geotags['GPSLongitude']
                        lon_ref = geotags['GPSLongitudeRef']
                        longitude = self.dms_to_decimal(*lon_tuple, lon_ref)

                    data.append([img_path, datetime_original, latitude, longitude, altitude])

        return pd.DataFrame(data, columns=['Filepath', 'DatetimeOriginal', 'Latitude', 'Longitude', 'Altitude'])

    def extract_and_assign_transects(self, folder_path, transect_file, output_csv):
        # Automatically fix backslashes in CSV and overwrite
        df = pd.read_csv(transect_file)
        if 'start_img' in df.columns and 'end_img' in df.columns:
            df['start_img'] = df['start_img'].astype(str).apply(lambda x: x.replace('\\', '/') if x else x)
            df['end_img']   = df['end_img'].astype(str).apply(lambda x: x.replace('\\', '/') if x else x)
            df.to_csv(transect_file, index=False)

        transect_assignment = pd.read_csv(transect_file)
        metadata = self.extract_metadata_from_folder(folder_path)
        metadata['Transect'] = 'NA'

        for index, row in transect_assignment.iterrows():
            start_time = None
            end_time = None

            # If columns exist for start_img/end_img
            if 'start_img' in row and 'end_img' in row and \
               pd.notna(row['start_img']) and pd.notna(row['end_img']):
                start_time_entries = metadata.loc[metadata['Filepath'] == row['start_img'], 'DatetimeOriginal'].values
                end_time_entries   = metadata.loc[metadata['Filepath'] == row['end_img'], 'DatetimeOriginal'].values
                if start_time_entries.size > 0 and end_time_entries.size > 0:
                    start_time = start_time_entries[0]
                    end_time   = end_time_entries[0]

            # Fallback if times are present
            if (start_time is None or end_time is None) and \
               'start_time' in row and 'end_time' in row:
                start_time = row['start_time']
                end_time   = row['end_time']

            if not (start_time and end_time):
                continue

            mask = (metadata['DatetimeOriginal'] >= str(start_time)) & \
                   (metadata['DatetimeOriginal'] <= str(end_time))
            metadata.loc[mask, 'Transect'] = row.get('transect_id', 'NA')

        metadata.to_csv(output_csv, index=False)
        return output_csv

    def kml_to_csv(self, kml_filepath, csv_filepath):
        tree = ET.parse(kml_filepath)
        root_ = tree.getroot()

        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        ns_ext = {'gx': 'http://www.google.com/kml/ext/2.2'}

        coordinates = []
        timestamps = []

        for placemark in root_.findall(".//kml:Placemark", ns):
            coords = placemark.findall(".//gx:coord", ns_ext)
            whens = placemark.findall(".//kml:when", ns)
            for coord, when_elem in zip(coords, whens):
                coordinate = coord.text.strip().split(' ')
                timestamp = when_elem.text
                coordinates.append(coordinate)
                timestamps.append(timestamp)

        df = pd.DataFrame(coordinates, columns=["Longitude", "Latitude", "Altitude"])
        df["Datetime"] = timestamps
        df.to_csv(csv_filepath, index=False)

    def integrate_csv_data(self):
        csv1 = pd.read_csv(self.final_metadata_csv.get())
        csv2_path = os.path.splitext(self.kml_file.get())[0] + '.csv'
        if not os.path.exists(csv2_path):
            return

        csv2 = pd.read_csv(csv2_path)
        csv1['Datetime'] = pd.to_datetime(csv1['DatetimeOriginal'], format='%Y:%m:%d %H:%M:%S', errors='coerce')
        csv2['Datetime'] = pd.to_datetime(csv2['Datetime'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce')
        csv1['Timestamp'] = csv1['Datetime'].apply(lambda x: x.timestamp() if not pd.isnull(x) else np.nan)
        csv2['Timestamp'] = csv2['Datetime'].apply(lambda x: x.timestamp() if not pd.isnull(x) else np.nan)

        def find_closest(row):
            time_diff = (csv2['Timestamp'] - row['Timestamp']).abs()
            closest_idx = time_diff.idxmin()
            closest_time_diff = time_diff[closest_idx]
            if closest_time_diff <= 3:
                return csv2.loc[closest_idx, ['Latitude', 'Longitude', 'Altitude']]
            else:
                return pd.Series([np.nan, np.nan, np.nan], index=['Latitude', 'Longitude', 'Altitude'])

        closest_values = csv1.apply(find_closest, axis=1)
        csv1[['LatitudeNew', 'LongitudeNew', 'AltitudeNew']] = closest_values
        csv1.to_csv(os.path.splitext(self.final_metadata_csv.get())[0] + '_updated.csv', index=False)

    def crop_images_based_on_transect(self, final_metadata_csv, input_folder, output_folder, crop_amount=125):
        import concurrent.futures
        import threading

        def decimal_to_dms(decimal):
            degrees = int(decimal)
            minutes = int((decimal - degrees) * 60)
            seconds = ((decimal - degrees - minutes / 60) * 3600)
            return ((degrees, 1), (minutes, 1), (int(seconds * 1000), 1000))

        # Load metadata
        updated_csv_path = os.path.join(os.path.dirname(final_metadata_csv), 'final_metadata_updated.csv')
        if os.path.exists(updated_csv_path):
            metadata = pd.read_csv(updated_csv_path)
        else:
            metadata = pd.read_csv(final_metadata_csv)

        # Filter valid images
        metadata['Altitude'] = pd.to_numeric(metadata['Altitude'], errors='coerce')
        valid_images = metadata[
            metadata['Transect'].notna() &
            (metadata['Transect'] != 'NA') &
            (metadata['Altitude'] >= float(self.min_altitude.get())) &
            (metadata['Altitude'] <= float(self.max_altitude.get()))
            ].copy()

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        print(f"Number of images to be cropped: {len(valid_images)}")

        # 1) Assign all new filenames in a single pass (no threading)
        if not hasattr(self, 'process_image_count_0'):
            self.process_image_count_0 = 0
        if not hasattr(self, 'process_image_count_1'):
            self.process_image_count_1 = 0

        for idx, row in valid_images.iterrows():
            folder_name = os.path.basename(os.path.dirname(row['Filepath']))
            if folder_name == '0':
                self.process_image_count_0 += 1
                img_count = self.process_image_count_0
                prefix = '0'
            elif folder_name == '1':
                self.process_image_count_1 += 1
                img_count = self.process_image_count_1
                prefix = '1'
            else:
                # If not in folder "0" or "1", skip naming
                valid_images.at[idx, 'NewFilename'] = None
                continue

            new_filename = f"{prefix}_000_00_{img_count:03d}.jpg"
            valid_images.at[idx, 'NewFilename'] = new_filename

        # 2) Parallelize cropping only, using the pre-assigned filenames
        def process_single_image(idx, row):
            if not row['NewFilename']:
                return (idx, None)  # skipped images

            image_path = row['Filepath']
            if not os.path.exists(image_path):
                return (idx, None)

            img = Image.open(image_path)
            width, height = img.size
            new_dimensions = (crop_amount, crop_amount, width - crop_amount, height - crop_amount)
            cropped_img = img.crop(new_dimensions)

            try:
                exif_data = piexif.load(img.info.get("exif", b""))
            except:
                exif_data = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}

            # Embed new lat/lon/alt if columns are present
            if 'LatitudeNew' in row and not pd.isna(row['LatitudeNew']):
                gps_ifd = {
                    piexif.GPSIFD.GPSLatitudeRef: 'S' if row['LatitudeNew'] < 0 else 'N',
                    piexif.GPSIFD.GPSLatitude: decimal_to_dms(abs(row['LatitudeNew'])),
                    piexif.GPSIFD.GPSLongitudeRef: 'W' if row['LongitudeNew'] < 0 else 'E',
                    piexif.GPSIFD.GPSLongitude: decimal_to_dms(abs(row['LongitudeNew'])),
                    piexif.GPSIFD.GPSAltitudeRef: 0,
                    piexif.GPSIFD.GPSAltitude: (int(abs(row['AltitudeNew']) * 1000), 1000),
                }
                exif_data['GPS'] = gps_ifd

            output_path = os.path.join(output_folder, row['NewFilename'])
            cropped_img.save(output_path, quality=100, exif=piexif.dump(exif_data))

            return (idx, output_path)

        new_filepaths = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_single_image, idx, row): idx for idx, row in valid_images.iterrows()}
            for fut in concurrent.futures.as_completed(futures):
                i, out_path = fut.result()
                if out_path:
                    new_filepaths[i] = out_path
                    print(f"Cropped: {out_path}, Transect: {valid_images.loc[i, 'Transect']}")

        # 3) Update main metadata with new filepaths
        for i, path_ in new_filepaths.items():
            metadata.loc[i, 'NewFilepath'] = path_

        metadata.to_csv(final_metadata_csv, index=False)
        metadata.to_csv(os.path.splitext(final_metadata_csv)[0] + '_updated_filepath.csv', index=False)
        print(f"Cropping completed. Cropped images are saved in '{output_folder}'.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMetadataGUI(root)
    root.mainloop()
