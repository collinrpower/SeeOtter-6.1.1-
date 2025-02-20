# SeeOtter User Guide: Comprehensive Workflow Explanation

## 1. Organize and Backup Data

### 1.1. Backup Camera Files

**Why is this step important?**  
- Raw aerial imagery is the foundation of the SeeOtter workflow.  
- Preserving file integrity prevents data loss from hardware failure, corruption, or accidental deletion.  
- A structured backup strategy ensures unaltered original files for future analysis.

**How to perform this step?**

**Automated Backup (Preferred Method)**  
1. Run `Backup_Images.py` to automate the backup process.  
2. The script prompts for:  
   - Number of backups (minimum 3 drives recommended)  
   - Destination folders for backups  
3. The script systematically copies image files from camera storage to the chosen backup destinations.

**Manual Backup (Alternative Method)**  
1. Copy raw imagery files manually onto at least three separate physical drives.  
2. Use structured naming conventions, for example:  
   `[Project_Name]_[Survey_Date]_[Camera_ID]_[Location]`  
3. Example directory structure:  
    /Backups/Survey2024/  
        ├── ExternalDrive1/  
        ├── ExternalDrive2/  
        ├── ExternalDrive3/  

**Verification and Integrity Check**  
- Confirm file sizes and counts match the originals.  
- Use checksums (e.g., `md5sum` or `sha256sum`) to verify data integrity.  
- Periodically test backups by accessing files to ensure readability.

---

### 1.2. Move Image Files into '0' and '1' Camera Folders

**Why is this step important?**  
- Dual-camera systems (or paired lenses) produce overlapping images.  
- Separating images into `0` and `1` folders helps organize and prevents duplicate processing.  
- Ensures correct transect assignments later on.

**How to perform this step?**

**For Non-Waldo Cameras (Generic Cameras)**  
1. Create a directory structure, for example:  
    /BaseFolder/Location/Camera/Year/MM_DD/  
        ├── 0/  
        ├── 1/  
2. Move images manually or use scripts to place them into the correct folder.

**For Waldo Cameras (Advanced Multi-Lens Systems)**  
1. Sort images automatically by file naming convention (e.g., files starting with `0` go to folder `0`, and so on).  
2. Run `Sort_Waldo_Camera_Images.py` to automate the sorting process.

**Verification and Quality Check**  
- Open a random selection of images from both folders to ensure correct sorting.  
- Compare timestamps to confirm sequential alignment.  
- Check file counts in each folder to identify missing or misplaced images.

---

## 2. Preprocess Images

### 2.1. Extract Image Metadata and Verify Data Quality

**Purpose**  
- Gather timestamps, latitude, longitude, and altitude from EXIF data for each image.  
- Ensures spatial accuracy and seamless integration with GIS tools.  
- Prevents errors from missing or incorrect geotagging.

**Steps**  
1. Run `Image_GPS_extract.py` to extract EXIF data.  
2. The script outputs a CSV with file path, `DatetimeOriginal`, latitude, longitude, and altitude (if available).  
3. Inspect the CSV to confirm valid timestamps/GPS coordinates.  
4. Compare to KML/SHP files if available to detect inconsistencies.

---

### 2.2. Assign Images to Transects

**Purpose**  
- Each image must be assigned to a specific transect for accurate data organization.  
- Prevents overlaps, gaps, and manual errors in assigning images to survey segments.

**Steps**  
1. Use the **Transect Assignment Template (CSV)** with columns:  
   - `transect_id`  
   - `start_img`  
   - `end_img`  
   - `start_time`  
   - `end_time`  
2. (Optional) Use a map-based tool to select start/end images interactively.  
3. Verify no overlaps or gaps exist between transects, then save the assignment file.

---

### 2.3. Classify Images as Land or Water

**Purpose**  
- Focus the model on water images where sea otters are likely found.  
- Filtering out land images improves detection accuracy and reduces processing time.

**Steps**  
1. Run the Land vs Water Image Classifier (`app.py`).  
2. Load the pre-trained deep learning model.  
3. The classifier outputs predictions for each image in the selected folder.  
4. Review/adjust low-confidence predictions.  
5. Save the final CSV classification report (only water images proceed).

---

### 2.4. Run Preprocessing

**Purpose**  
- Assign images to their transects, apply GPS corrections, and optionally crop images.  
- Ensures consistent formatting for the detection pipeline.

**Steps**  
1. Run `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`.  
2. Process images per transect assignments; correct GPS offsets with external KML.  
3. Outputs cropped images to the `cropped_images_on_tx` folder.  
4. Verify all images retain necessary features and correct GPS coordinates.

---

## 3. AI-Assisted Object Detection

### 3.1. Change Model Weights (Optional)

**Why is this step important?**  
- Using updated YOLO `.pt` files can enhance detection accuracy.  
- Allows for incorporating newly trained models specific to sea otter detection.

**How to perform this step?**  
1. Choose the new YOLO `.pt` file.  
2. Replace the existing `best.pt` in the `ModelWeights` folder.  
3. Test on a small batch of images to confirm performance.

---

### 3.2. Edit Otter Checker Config

**Why is this step important?**  
- Otter Checker must match the new model's detection classes and labels.  
- Ensures correct interpretation and display of model outputs.

**How to perform this step?**  
1. Open the Otter Checker config file.  
2. Update image tags/annotation categories for the new model.  
3. Run a test detection to confirm annotations match expectations.

---

### 3.3. Run SeeOtter Processing

**Why is this step important?**  
- SeeOtter uses the configured model to detect sea otters in preprocessed images.  
- Outputs preliminary bounding boxes and confidence scores.

**How to perform this step?**  
1. Launch `SeeOtter.exe`.  
2. Point to the `cropped_images_on_tx` folder as the input.  
3. Run the processing pipeline; check the output folder for detection results.  
4. Inspect a random sample for bounding box accuracy.

---

### 3.4. Prediction Validation

**Why is this step important?**  
- Human reviewers confirm or correct the AI’s detections.  
- Identifies false positives/negatives before final reporting.

**How to perform this step?**  
1. Examine bounding boxes and confidence scores in each image.  
2. Label detections as **Correct**, **Incorrect**, or **Ambiguous**.  
3. Append these validations to an annotation file, preserving each detection’s status.

---

### 3.5. Final Processing

**Why is this step important?**  
- Produces cleaned, validated results suitable for population counts and analysis.  
- Creates reports on survey effort and generates geospatial outputs.

**How to perform this step?**  
1. Run `SeeOtter_post_pro_count_and_split_odd_even.py` to organize validated detections.  
2. **Data Cleanup**: Remove invalid/incomplete entries.  
3. **Final Validation**: Confirm all detections have been addressed.  
4. **Population Count**: Tally validated sea otter detections.  
5. **Survey Effort**: Generate metrics (images processed, time per transect).  
6. **Geospatial Data**: Produce a shapefile of validated detection locations.  
7. Verify CSV/shapefile outputs, population counts, and completeness before final use.
