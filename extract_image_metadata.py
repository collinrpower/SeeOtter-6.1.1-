import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd


def get_exif_data(img):
    """
    Extracts EXIF data from an image and returns a dictionary with tag names as keys.
    """
    exif_data = {}
    try:
        raw_exif = img._getexif()
        if raw_exif:
            for tag, value in raw_exif.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
    except Exception as e:
        print(f"Error retrieving EXIF data: {e}")
    return exif_data


def get_geotagging(exif):
    """
    Extracts GPS-related data from the EXIF dictionary.
    Returns a dictionary of GPS tags if available.
    """
    if not exif:
        return {}
    gps_info = exif.get("GPSInfo", {})
    geotagging = {}
    for key in gps_info.keys():
        decoded_key = GPSTAGS.get(key, key)
        geotagging[decoded_key] = gps_info[key]
    return geotagging


def dms_to_decimal(dms, ref):
    """
    Converts a tuple of degrees, minutes, seconds to decimal format.
    Handles values stored as rational numbers (tuple of numerator/denominator).
    """
    try:
        if not dms or len(dms) != 3:
            return 'NA'
        # Handle potential rational numbers
        degrees = dms[0][0] / dms[0][1] if isinstance(dms[0], tuple) else dms[0]
        minutes = dms[1][0] / dms[1][1] if isinstance(dms[1], tuple) else dms[1]
        seconds = dms[2][0] / dms[2][1] if isinstance(dms[2], tuple) else dms[2]
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception as e:
        print(f"Error converting DMS to decimal: {e}")
        return 'NA'


def extract_metadata_from_image(img_path):
    """
    Extracts metadata from a single image file and returns a dictionary with
    standardized keys: Filepath, DatetimeOriginal, Latitude, Longitude, Altitude.
    """
    metadata = {
        'Filepath': img_path,
        'DatetimeOriginal': 'NA',
        'Latitude': 'NA',
        'Longitude': 'NA',
        'Altitude': 'NA'
    }
    try:
        img = Image.open(img_path)
        exif = get_exif_data(img)

        # Attempt to get the original timestamp from common tags
        datetime_original = exif.get("DateTimeOriginal") or exif.get("DateTime")
        if datetime_original:
            metadata['DatetimeOriginal'] = datetime_original

        # Process GPS information
        geotags = get_geotagging(exif)
        if geotags:
            if "GPSLatitude" in geotags and "GPSLatitudeRef" in geotags:
                metadata['Latitude'] = dms_to_decimal(geotags["GPSLatitude"], geotags["GPSLatitudeRef"])
            if "GPSLongitude" in geotags and "GPSLongitudeRef" in geotags:
                metadata['Longitude'] = dms_to_decimal(geotags["GPSLongitude"], geotags["GPSLongitudeRef"])
            if "GPSAltitude" in geotags:
                altitude = geotags["GPSAltitude"]
                # Some cameras return altitude as a rational number
                if isinstance(altitude, tuple):
                    metadata['Altitude'] = altitude[0] / altitude[1]
                else:
                    metadata['Altitude'] = altitude
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
    return metadata


def extract_metadata_from_folder(folder_path):
    """
    Walks through the provided folder and extracts metadata from all image files.
    Returns a DataFrame with standardized columns.
    """
    data = []
    for root_dir, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(root_dir, file)
                metadata = extract_metadata_from_image(img_path)
                data.append([
                    metadata['Filepath'],
                    metadata['DatetimeOriginal'],
                    metadata['Latitude'],
                    metadata['Longitude'],
                    metadata['Altitude']
                ])
    return pd.DataFrame(data, columns=['Filepath', 'DatetimeOriginal', 'Latitude', 'Longitude', 'Altitude'])


class ImageMetadataExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Extract Image Metadata and Verify Data Quality")
        self.folder_path = tk.StringVar()
        self.output_csv = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        instruction_text = (
            "Extract Image Metadata and Verify Data Quality\n"
            "a. Select Input Folder\n"
            "b. Specify output CSV file (or use default in the input folder)\n"
            "c. The CSV will include Image Filepaths, Timestamps, Latitudes, Longitudes, and Altitudes"
        )
        tk.Label(self.root, text=instruction_text, justify="left").grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        tk.Label(self.root, text="Input Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.folder_path, width=50).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        tk.Button(self.root, text="Browse", command=self.browse_folder).grid(row=1, column=2, padx=10, pady=5)
        tk.Label(self.root, text="Output CSV:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.output_csv, width=50).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        tk.Button(self.root, text="Browse", command=self.browse_csv).grid(row=2, column=2, padx=10, pady=5)
        tk.Button(self.root, text="Extract Metadata", command=self.run_extraction).grid(row=3, column=0, columnspan=3,
                                                                                        padx=10, pady=10)
        self.folder_path.trace_add("write", self.update_output_csv)

    def update_output_csv(self, *args):
        if self.folder_path.get():
            self.output_csv.set(os.path.join(self.folder_path.get(), "original_gps_metadata.csv"))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def browse_csv(self):
        csv_file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if csv_file:
            self.output_csv.set(csv_file)

    def run_extraction(self):
        input_folder = self.folder_path.get()
        output_csv = self.output_csv.get()
        if not input_folder:
            messagebox.showerror("Error", "Please select an input folder.")
            return
        if not output_csv:
            messagebox.showerror("Error", "Please specify an output CSV file path.")
            return
        try:
            df = extract_metadata_from_folder(input_folder)
            # Force consistent CSV formatting across systems:
            df.to_csv(output_csv, index=False, encoding='utf-8', lineterminator='\n')
            messagebox.showinfo("Success", f"Metadata extracted and saved to {output_csv}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during extraction: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMetadataExtractorApp(root)
    root.mainloop()
