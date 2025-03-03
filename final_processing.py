import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def find_all_tags_as_df(json_file_path):
    with open(json_file_path, 'r') as f:
        raw_data = f.read()
        data = json.loads(raw_data)
        if isinstance(data, str):  # Handle nested JSON-as-string
            data = json.loads(data)

    images = data.get('images', [])
    all_tags = set()
    for img in images:
        for tag_entry in img.get('tags', {}).get('tags', []):
            all_tags.add(tag_entry.get('name', ''))
    all_tags = sorted(all_tags)

    # Build DataFrame with columns for each tag
    rows = []
    for img in images:
        file_name = img.get('file_name', 'Unknown')
        image_tags = {t.get('name', '') for t in img.get('tags', {}).get('tags', [])}
        row_dict = {'Image Name': file_name}
        for tag in all_tags:
            row_dict[tag] = "TRUE" if tag in image_tags else "FALSE"
        rows.append(row_dict)

    return pd.DataFrame(rows)

class FinalProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Final Processing")
        self.created_folder_path = tk.StringVar()
        self.transect_csv_path = None
        self.json_tags_path = None
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Images Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.created_folder_path, width=50).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        tk.Button(self.root, text="Browse", command=self.browse_created_folder).grid(row=0, column=2, padx=10, pady=5)

        tk.Button(self.root, text="Run Final Processing", command=self.run_processing).grid(row=1, column=1, padx=10, pady=10)

    def browse_created_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.created_folder_path.set(folder)

    def add_transect_column(self, final_df):
        if not self.transect_csv_path:
            return final_df
        df_transect = pd.read_csv(self.transect_csv_path)
        if 'NewFilepath' in df_transect.columns and 'Transect' in df_transect.columns:
            final_df = final_df.merge(df_transect[['NewFilepath','Transect']],
                                      left_on='FilePath', right_on='NewFilepath', how='left')
            final_df.drop(columns='NewFilepath', inplace=True)
        return final_df

    def process_data_final(self, df_predictions, df_otter_count):
        df_otter_count['SortOrder'] = df_otter_count['FilePath'].isin(df_predictions['FilePath']).astype(int)
        df_otter_count = (df_otter_count
                          .sort_values(by=['FilePath','SortOrder'], ascending=[True,False])
                          .drop_duplicates(subset='FilePath')
                          .drop(columns='SortOrder'))

        correct_df = df_predictions[df_predictions['ValidationState'] == "CORRECT"]
        pivot_df = pd.pivot_table(correct_df, values='ImageID', index='FilePath',
                                  columns='PredictionCategoryName', aggfunc='count', fill_value=0)
        pivot_df['Total'] = pivot_df.sum(axis=1)
        if 'o' in pivot_df.columns and 'p' in pivot_df.columns:
            pivot_df['o+p'] = pivot_df['o'] + pivot_df['p']
        else:
            pivot_df['o+p'] = pivot_df['o'] if 'o' in pivot_df.columns else 0
        pivot_df.reset_index(inplace=True)

        merged_counts_df = pd.merge(df_otter_count[['FilePath']], pivot_df, on='FilePath', how='left').fillna(0)
        merged_df = pd.merge(merged_counts_df, df_otter_count, on='FilePath', how='left')

        needed_cols = [
            'ImageID', 'Datetime', 'FilePath', 'CameraLatitude', 'CameraLongitude', 'CameraAltitude',
            'ImageCorner1Lat', 'ImageCorner1Lon', 'ImageCorner2Lat', 'ImageCorner2Lon',
            'ImageCorner3Lat', 'ImageCorner3Lon', 'ImageCorner4Lat', 'ImageCorner4Lon'
        ]
        final_df = merged_df[needed_cols + list(pivot_df.columns.drop('FilePath'))]

        # Calculate additional columns
        final_df['GSD'] = ((35.482 * final_df['CameraAltitude'] * 100) / (50 * 8563))
        final_df['Width_m'] = (final_df['GSD'] * 8563 / 100)
        final_df['Height_m'] = (final_df['GSD'] * 5667 / 100)
        final_df['Coverage_sqkm'] = final_df['Width_m'] * final_df['Height_m'] / 1_000_000

        final_df = self.add_transect_column(final_df)

        # Merge tags
        if self.json_tags_path is not None:
            tags_df = find_all_tags_as_df(self.json_tags_path)
            # Match base filename
            final_df['BaseFileName'] = final_df['FilePath'].apply(os.path.basename)
            tags_df.rename(columns={'Image Name': 'BaseFileName'}, inplace=True)
            final_df = final_df.merge(tags_df, on='BaseFileName', how='left')
            final_df.drop(columns='BaseFileName', inplace=True)

        return final_df

    def run_processing(self):
        # Select JSON for tags
        self.json_tags_path = filedialog.askopenfilename(
            title="Select JSON file with tags",
            filetypes=[("JSON files", "*.json")]
        )
        if not self.json_tags_path:
            messagebox.showerror("Error", "No JSON file selected.")
            return

        # Select transect assignment CSV
        self.transect_csv_path = filedialog.askopenfilename(
            title="Select the transect assignment CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if not self.transect_csv_path:
            messagebox.showerror("Error", "No transect CSV selected.")
            return

        # Select results_all_predictions.csv
        input_filepath = filedialog.askopenfilename(
            title="Select 'results_all_predictions.csv':",
            filetypes=[("CSV files", "*results_all_predictions.csv")]
        )
        if not input_filepath:
            messagebox.showerror("Error", "No 'results_all_predictions.csv' selected.")
            return

        # Select results_distinct_otter_count_by_image.csv
        distinct_filepath = filedialog.askopenfilename(
            title="Select 'results_distinct_otter_count_by_image.csv':",
            filetypes=[("CSV files", "*results_distinct_otter_count_by_image.csv")]
        )
        if not distinct_filepath:
            messagebox.showerror("Error", "No 'results_distinct_otter_count_by_image.csv' selected.")
            return

        df_predictions = pd.read_csv(input_filepath, low_memory=False)
        df_otter_count = pd.read_csv(distinct_filepath, low_memory=False)
        final_df = self.process_data_final(df_predictions, df_otter_count)

        # Rename columns and save
        output_filename = input_filepath.rsplit('.', 1)[0] + '_processed.csv'
        final_df = final_df.rename(columns={
            'Datetime': 'PHOTO_TIMESTAMP',
            'CameraAltitude': 'ALTITUDE',
            'CameraLatitude': 'LATITUDE_WGS84',
            'CameraLongitude': 'LONGITUDE_WGS84',
            'o': 'COUNT_ADULT',
            'p': 'COUNT_PUP',
            'o+p': 'COUNT_ALL_OTTERS'
        })
        final_df['PHOTO_TIMESTAMP'] = final_df['PHOTO_TIMESTAMP'].str.replace(':', '-', 2)
        final_df.to_csv(output_filename, index=False)

        # Odd ImageID
        odd_df = final_df[final_df['ImageID'] % 2 != 0]
        odd_output_filename = input_filepath.rsplit('.', 1)[0] + '_odd_processed.csv'
        odd_df.to_csv(odd_output_filename, index=False)

        # Even ImageID
        even_df = final_df[final_df['ImageID'] % 2 == 0]
        even_output_filename = input_filepath.rsplit('.', 1)[0] + '_even_processed.csv'
        even_df.to_csv(even_output_filename, index=False)

        msg = (
            f"Output Files:\n\nAll records:\n{output_filename}\nImages: {len(final_df)}\n"
            f"o+p count: {final_df['COUNT_ALL_OTTERS'].sum()}\n\n"
            f"Odd ImageIDs:\n{odd_output_filename}\nImages: {len(odd_df)}\n"
            f"o+p count: {odd_df['COUNT_ALL_OTTERS'].sum()}\n\n"
            f"Even ImageIDs:\n{even_output_filename}\nImages: {len(even_df)}\n"
            f"o+p count: {even_df['COUNT_ALL_OTTERS'].sum()}"
        )
        messagebox.showinfo("Processing Complete", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinalProcessingApp(root)
    root.mainloop()
