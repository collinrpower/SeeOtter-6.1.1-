import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import geopandas as gpd
import contextily as ctx
from geopy.distance import geodesic
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        vscrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        hscrollbar = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: canvas.configure(scrollregion=canvas.bbox("all"), width=e.width))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.pack(side="right", fill="y")
        hscrollbar.pack(side="bottom", fill="x")

class AssignImagesToTransectsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assign Images to Transects")
        self.csv_data = pd.DataFrame()
        self.gps_coords = []  # List of (lat, lon)
        self.filepaths = []   # List of tuples (filepath, datetime)
        self.selected_filepaths = []
        self.selected_points = []  # Will store indices from gps_coords
        self.hover_popup = None
        self.hover_images = []  # To keep references to PhotoImage objects
        self.enable_thumbnail_popup = True  # Toggle for thumbnail popup
        self.create_widgets()

    def create_widgets(self):
        instruction_text = (
            "4. Assign images to transects\n"
            "a. Use the tx_assignment_template.csv or create a csv with 5 columns\n"
            "b. Fill ‘transect_id’ with the names of your proposed transects\n"
            "c. For each transect set your start and end points\n"
            "   i. Use file paths or times for start and end points"
        )
        tk.Label(self.root, text=instruction_text, justify="left").pack(padx=10, pady=10)
        tk.Button(self.root, text="Load original_gps_metadata.csv", command=self.load_metadata).pack(padx=10, pady=5)
        self.csv_container = ScrollableFrame(self.root)
        self.csv_container.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Button(self.root, text="Load Assignment CSV", command=self.load_csv).pack(padx=10, pady=5)
        tk.Button(self.root, text="Save CSV", command=self.save_csv).pack(padx=10, pady=5)
        tk.Button(self.root, text="Create Default CSV", command=self.create_default_csv).pack(padx=10, pady=5)
        tk.Button(self.root, text="Add Row", command=self.add_row).pack(padx=10, pady=5)

    def load_metadata(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*original_gps_metadata.csv")],
            title="Select original_gps_metadata.csv"
        )
        if not file_path:
            return
        df = pd.read_csv(file_path)
        required_columns = ['Filepath', 'DatetimeOriginal', 'Latitude', 'Longitude']
        if not all(col in df.columns for col in required_columns):
            messagebox.showerror("Error", f"CSV must contain: {required_columns}")
            return
        self.filepaths = list(zip(df['Filepath'], df['DatetimeOriginal']))
        self.gps_coords = list(zip(df['Latitude'], df['Longitude']))
        self.metadata_dir = os.path.dirname(file_path)  # Save the directory path
        messagebox.showinfo("Success", "original_gps_metadata.csv loaded successfully!")

    def save_csv(self):
        if not hasattr(self, 'metadata_dir'):
            messagebox.showerror("Error", "Metadata not loaded. Please load original_gps_metadata.csv first.")
            return
        save_path = os.path.join(self.metadata_dir, "transect_assignment.csv")
        sorted_df = self.csv_data.sort_values(
            by='start_time') if 'start_time' in self.csv_data.columns else self.csv_data
        sorted_df.to_csv(save_path, index=False)
        messagebox.showinfo("Success", f"CSV file saved successfully at {save_path}!")
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*original_gps_metadata.csv")], title="Select original_gps_metadata.csv")
        if not file_path:
            return
        df = pd.read_csv(file_path)
        required_columns = ['Filepath', 'DatetimeOriginal', 'Latitude', 'Longitude']
        if not all(col in df.columns for col in required_columns):
            messagebox.showerror("Error", f"CSV must contain: {required_columns}")
            return
        self.filepaths = list(zip(df['Filepath'], df['DatetimeOriginal']))
        self.gps_coords = list(zip(df['Latitude'], df['Longitude']))
        messagebox.showinfo("Success", "final_metadata.csv loaded successfully!")

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        self.csv_data = pd.read_csv(file_path)
        self.display_csv()


    def create_default_csv(self):
        default_columns = ['start_img', 'end_img', 'transect_id', 'start_time', 'end_time']
        self.csv_data = pd.DataFrame(columns=default_columns)
        self.display_csv()

    def display_csv(self):
        for widget in self.csv_container.scrollable_frame.winfo_children():
            widget.destroy()
        columns = list(self.csv_data.columns)
        for col_num, column in enumerate(columns):
            label = tk.Label(self.csv_container.scrollable_frame, text=column, borderwidth=1, relief="solid")
            label.grid(row=0, column=col_num, sticky="nsew")
        self.csv_widgets = []
        for i, row in self.csv_data.iterrows():
            row_widgets = []
            for j, value in enumerate(row):
                entry = tk.Entry(self.csv_container.scrollable_frame)
                entry.grid(row=i + 1, column=j, sticky="nsew")
                entry.insert(0, value)
                row_widgets.append(entry)
            self.csv_widgets.append(row_widgets)

    def add_row(self):
        self.select_filepaths_for_new_row()

    def select_filepaths_for_new_row(self):
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select File Paths for New Row")
        tk.Radiobutton(selection_window, text="Search by Filename", value="Search",
                       command=lambda: self.show_search_widgets(selection_window)).pack(anchor='w', padx=10, pady=5)
        tk.Radiobutton(selection_window, text="Select from Map", value="Map",
                       command=lambda: self.show_map(selection_window)).pack(anchor='w', padx=10, pady=5)
        self.show_search_widgets(selection_window)

    def show_search_widgets(self, selection_window):
        for widget in selection_window.winfo_children():
            if isinstance(widget, tk.Entry) or isinstance(widget, tk.Listbox) or isinstance(widget, tk.Label):
                widget.destroy()
        tk.Label(selection_window, text="Search by Filename:").pack(padx=10, pady=5)
        search_entry = tk.Entry(selection_window, width=50)
        search_entry.pack(padx=10, pady=5)
        tk.Label(selection_window, text="Select the file paths you want to use (Max 2):").pack(padx=10, pady=5)
        self.first_image_label = tk.Label(selection_window, text="First Image: None")
        self.first_image_label.pack(padx=10, pady=5)
        self.last_image_label = tk.Label(selection_window, text="Last Image: None")
        self.last_image_label.pack(padx=10, pady=5)
        self.filtered_filepaths = self.filepaths.copy()
        self.filepath_listbox = tk.Listbox(selection_window, selectmode=tk.MULTIPLE, width=100, height=20)
        self.update_file_listbox()
        self.filepath_listbox.pack(padx=10, pady=5)
        search_entry.bind("<KeyRelease>", lambda event: self.filter_filepaths(search_entry.get()))
        self.filepath_listbox.bind("<<ListboxSelect>>", self.update_image_labels)
        tk.Button(selection_window, text="Confirm Selection",
                  command=lambda: self.confirm_new_row_filepaths(selection_window)).pack(padx=10, pady=10)

    def filter_filepaths(self, search_text):
        search_text = search_text.lower()
        filtered = [(fp, dt) for fp, dt in self.filepaths if search_text in os.path.basename(fp).lower()]
        self.filtered_filepaths = self.selected_filepaths + [item for item in filtered if item not in self.selected_filepaths]
        self.update_file_listbox()

    def update_file_listbox(self):
        self.filepath_listbox.delete(0, tk.END)
        for filepath, datetime_original in self.filtered_filepaths:
            display_text = f"{filepath} | {datetime_original}"
            self.filepath_listbox.insert(tk.END, display_text)
        for i, item in enumerate(self.filtered_filepaths):
            if item in self.selected_filepaths:
                self.filepath_listbox.selection_set(i)

    def update_image_labels(self, event):
        selected_indices = self.filepath_listbox.curselection()
        selected = [self.filtered_filepaths[i] for i in selected_indices]
        self.selected_filepaths = selected
        if len(selected) >= 1:
            self.first_image_label.config(text=f"First Image: {selected[0][0]}")
        else:
            self.first_image_label.config(text="First Image: None")
        if len(selected) >= 2:
            self.last_image_label.config(text=f"Last Image: {selected[1][0]}")
        else:
            self.last_image_label.config(text="Last Image: None")

    def fix_timestamp(self, ts):
        try:
            date_part, time_part = ts.split(" ", 1)
            if ":" in date_part and "-" not in date_part:
                fixed_date = date_part.replace(":", "-", 2)
                return fixed_date + " " + time_part
        except Exception:
            pass
        return ts

    def confirm_new_row_filepaths(self, selection_window):
        selected_indices = self.filepath_listbox.curselection()
        selected = [self.filtered_filepaths[i] for i in selected_indices]
        if len(selected) != 2:
            messagebox.showerror("Error", "Please select exactly two file paths.")
            return
        time0_fixed = self.fix_timestamp(selected[0][1])
        time1_fixed = self.fix_timestamp(selected[1][1])
        if pd.to_datetime(time0_fixed) <= pd.to_datetime(time1_fixed):
            start_filepath, end_filepath = selected[0], selected[1]
        else:
            start_filepath, end_filepath = selected[1], selected[0]
        new_row = {
            'start_img': start_filepath[0],
            'end_img': end_filepath[0],
            'transect_id': self.prompt_transect_name(),
            'start_time': start_filepath[1],
            'end_time': end_filepath[1]
        }
        self.csv_data = pd.concat([self.csv_data, pd.DataFrame([new_row])], ignore_index=True)
        self.display_csv()
        selection_window.destroy()

    def show_map(self, selection_window):
        for widget in selection_window.winfo_children():
            widget.destroy()
        if not self.gps_coords:
            messagebox.showerror("Error", "No GPS coordinates available for mapping.")
            return
        self.map_window = selection_window  # Save reference for hover popup

        # Create control frame for label and buttons.
        control_frame = tk.Frame(selection_window)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        selection_count_label = tk.Label(control_frame, text="Selected Points: 0/2", font=("Arial", 12))
        selection_count_label.pack(side=tk.LEFT, padx=10, pady=5)
        button_frame = tk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        tk.Button(button_frame, text="Reset Selection",
                  command=lambda: self.reset_selections(ax, fig, gdf, selection_count_label)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Confirm Selection",
                  command=lambda: self.confirm_selections(selection_window)).pack(side=tk.LEFT, padx=5, pady=5)
        # Add toggle for thumbnail popup
        self.popup_toggle_var = tk.BooleanVar(value=True)
        popup_check = tk.Checkbutton(control_frame, text="Enable Thumbnail Popup", variable=self.popup_toggle_var, command=self.toggle_thumbnail_popup)
        popup_check.pack(side=tk.RIGHT, padx=10, pady=5)

        # Create canvas frame below controls.
        canvas_frame = tk.Frame(selection_window)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        latitudes, longitudes = zip(*self.gps_coords)
        gdf = gpd.GeoDataFrame({'geometry': gpd.points_from_xy(longitudes, latitudes)}, crs='EPSG:4326')
        gdf = gdf.to_crs(epsg=3857)
        fig, ax = plt.subplots(figsize=(10, 8))
        gdf.plot(ax=ax, marker='o', color='blue', markersize=50, label='Images')
        try:
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add basemap: {e}")
            return
        ax.set_title("Select Start and End Points by Clicking on the Map", fontsize=16)
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.legend()

        # Precompute projected points (EPSG:3857) for hover detection.
        transformer2 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        projected_points = [transformer2.transform(lon, lat) for (lat, lon) in self.gps_coords]

        def on_hover(event):
            if not self.enable_thumbnail_popup:
                if self.hover_popup is not None:
                    self.hover_popup.destroy()
                    self.hover_popup = None
                return
            if event.inaxes != ax:
                if self.hover_popup is not None:
                    self.hover_popup.destroy()
                    self.hover_popup = None
                return
            hovered_index = None
            min_dist = float('inf')
            for i, pt in enumerate(projected_points):
                disp_pt = ax.transData.transform(pt)
                dist = ((disp_pt[0] - event.x)**2 + (disp_pt[1] - event.y)**2)**0.5
                if dist < 10 and dist < min_dist:
                    min_dist = dist
                    hovered_index = i
            if hovered_index is not None:
                close_indices = []
                for j, pt in enumerate(projected_points):
                    disp_pt = ax.transData.transform(pt)
                    if ((disp_pt[0] - event.x)**2 + (disp_pt[1] - event.y)**2)**0.5 < 10:
                        close_indices.append(j)
                if close_indices:
                    self.show_hover_popup(close_indices, event)
                else:
                    if self.hover_popup is not None:
                        self.hover_popup.destroy()
                        self.hover_popup = None
            else:
                if self.hover_popup is not None:
                    self.hover_popup.destroy()
                    self.hover_popup = None

        def on_click(event):
            if event.inaxes != ax:
                return
            xdata, ydata = event.xdata, event.ydata
            if xdata is None or ydata is None:
                return
            # Compute dynamic click buffer in meters:
            canvas_width, _ = fig.canvas.get_width_height()
            data_width = ax.get_xlim()[1] - ax.get_xlim()[0]  # width in meters (EPSG:3857)
            meters_per_pixel = data_width / canvas_width
            pixel_buffer = 10  # adjustable buffer in pixels
            dynamic_max_distance = pixel_buffer * meters_per_pixel

            click_lon, click_lat = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform(xdata,
                                                                                                            ydata)
            closest_coord, distance = self.find_closest_within_threshold((click_lat, click_lon),
                                                                         max_distance=dynamic_max_distance)
            if closest_coord:
                idx = self.gps_coords.index(closest_coord)
                if idx in self.selected_points:
                    return
                self.selected_points.append(idx)
                spwm = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform(closest_coord[1],
                                                                                                closest_coord[0])
                ax.scatter(spwm[0], spwm[1], marker='x', color='red', s=100)
                selection_count_label.config(text=f"Selected Points: {len(self.selected_points)}/2")
                fig.canvas.draw_idle()
        def zoom(event):
            if event.inaxes != ax or event.xdata is None or event.ydata is None:
                return
            base_scale = 1.1
            if event.button in ['up', 4]:
                scale_factor = 1 / base_scale
            elif event.button in ['down', 5]:
                scale_factor = base_scale
            else:
                scale_factor = 1
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            cur_width = cur_xlim[1] - cur_xlim[0]
            cur_height = cur_ylim[1] - cur_ylim[0]
            new_width = cur_width * scale_factor
            new_height = cur_height * scale_factor
            relx = (event.xdata - cur_xlim[0]) / cur_width
            rely = (event.ydata - cur_ylim[0]) / cur_height
            ax.set_xlim([event.xdata - new_width * relx, event.xdata + new_width * (1 - relx)])
            ax.set_ylim([event.ydata - new_height * rely, event.ydata + new_height * (1 - rely)])
            fig.canvas.draw_idle()

        def on_pan(event):
            if event.button == 1 and event.inaxes == ax:
                dx = event.xdata - on_pan.prev_x
                dy = event.ydata - on_pan.prev_y
                on_pan.prev_x, on_pan.prev_y = event.xdata, event.ydata
                cur_xlim = ax.get_xlim()
                cur_ylim = ax.get_ylim()
                ax.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
                ax.set_ylim(cur_ylim[0] - dy, cur_ylim[1] - dy)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect('scroll_event', zoom)
        fig.canvas.mpl_connect('button_press_event',
                               lambda e: setattr(on_pan, 'prev_x', e.xdata) or setattr(on_pan, 'prev_y', e.ydata))
        fig.canvas.mpl_connect('motion_notify_event', on_pan)
        fig.canvas.mpl_connect('motion_notify_event', on_hover)
        fig.canvas.mpl_connect('button_press_event', on_click)

        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_thumbnail_popup(self):
        self.enable_thumbnail_popup = self.popup_toggle_var.get()

    def show_hover_popup(self, indices, event):
        if self.hover_popup is not None:
            self.hover_popup.destroy()
        self.hover_popup = tk.Toplevel(self.map_window)
        self.hover_popup.overrideredirect(True)
        frame = tk.Frame(self.hover_popup, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)
        self.hover_images = []
        for idx in indices:
            filepath, _ = self.filepaths[idx]
            try:
                im = Image.open(filepath)
                im.thumbnail((570, 870), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(im)
                self.hover_images.append(photo)
                label = tk.Label(frame, image=photo, bg="white")
                label.pack(side="left", padx=2, pady=2)
            except Exception as e:
                print("Error loading image", filepath, e)
        self.hover_popup.geometry(f"+{event.x_root+10}+{event.y_root+10}")

    def reset_selections(self, ax, fig, gdf, selection_count_label):
        self.selected_points = []
        selection_count_label.config(text="Selected Points: 0/2")
        ax.cla()
        gdf.plot(ax=ax, marker='o', color='blue', markersize=50, label='Images')
        try:
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add basemap: {e}")
            return
        ax.set_title("Select Start and End Points by Clicking on the Map", fontsize=16)
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.legend()
        fig.canvas.draw_idle()

    def confirm_selections(self, selection_window):
        if len(self.selected_points) != 2:
            messagebox.showerror("Error", "Please select exactly two points before confirming.")
            return
        start_idx, end_idx = self.selected_points
        self.confirm_new_row_filepaths_from_coords(start_idx, end_idx)

    def find_closest_within_threshold(self, clicked_coord, max_distance=500):
        min_distance = float('inf')
        closest_coord = None
        for coord in self.gps_coords:
            distance = geodesic(clicked_coord, coord).meters
            if distance < min_distance:
                min_distance = distance
                closest_coord = coord
        if min_distance <= max_distance:
            return closest_coord, min_distance
        else:
            return None, None

    def confirm_new_row_filepaths_from_coords(self, start_index, end_index):
        fp1, time1 = self.filepaths[start_index]
        fp2, time2 = self.filepaths[end_index]
        time1_fixed = self.fix_timestamp(time1)
        time2_fixed = self.fix_timestamp(time2)
        if pd.to_datetime(time1_fixed) <= pd.to_datetime(time2_fixed):
            start_fp, start_time = fp1, time1
            end_fp, end_time = fp2, time2
        else:
            start_fp, start_time = fp2, time2
            end_fp, end_time = fp1, time1
        new_row = {
            'start_img': start_fp,
            'end_img': end_fp,
            'transect_id': self.prompt_transect_name(),
            'start_time': start_time,
            'end_time': end_time
        }
        self.csv_data = pd.concat([self.csv_data, pd.DataFrame([new_row])], ignore_index=True)
        self.display_csv()

    def prompt_transect_name(self):
        transect_name = simpledialog.askstring("Transect Name", "Enter the transect name:")
        return transect_name if transect_name else f"transect_{len(self.csv_data) + 1}"

if __name__ == "__main__":
    root = tk.Tk()
    app = AssignImagesToTransectsApp(root)
    root.mainloop()
