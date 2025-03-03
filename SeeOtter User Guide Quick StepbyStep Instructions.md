# SeeOtter User Guide: Quick Step-by-Step Instructions

## 1. Organize and Backup Data

### 1.1. Backup Camera Files

**Automated Backup (Preferred)**  
1. Run `Backup_Images.py`.  
2. Specify at least 3 backup drives.  
3. Choose destinations; script copies images from camera to backups.

**Manual Backup (Alternative)**  
1. Copy raw images to at least 3 physical drives.  
2. Use a structured naming convention:
   [Project_Name]_[Survey_Date]_[Camera_ID]_[Location]
3. Example directory structure:
   /Backups/Survey2024/
       ├── ExternalDrive1/
       ├── ExternalDrive2/
       ├── ExternalDrive3/

**Verification**  
- Check file counts/sizes.  
- Optionally use checksums (md5, sha256).  
- Periodically test access to backup files.

### 1.2. Move Image Files into '0' and '1' Camera Folders

**For Non-Waldo Cameras**  
1. Create a directory structure:
   /BaseFolder/Location/Camera/Year/MM_DD/
       ├── 0/
       ├── 1/
2. Manually move images or use scripts.

**For Waldo Cameras**  
1. If filename starts with "0", move to folder `0`; if "1", move to folder `1`.  
2. Run `Sort_Waldo_Camera_Images.py` for automation.

**Verification**  
- Open random images from both folders.  
- Confirm correct sequence via timestamps.  
- Check file counts match expectations.

---

## 2. Preprocess Images

### 2.1. Extract Metadata and Verify Quality

1. Run `Image_GPS_extract.py`.  
2. Extracts file path, DatetimeOriginal, Latitude, Longitude, Altitude to a CSV.  
3. Inspect the CSV for correctness.  
4. Use KML/SHP if available for spatial reference.

### 2.2. Assign Images to Transects

1. Use a CSV with columns: `transect_id`, `start_img`, `end_img`, `start_time`, `end_time`.  
2. (Optional) Manually pick start/end images in a map-based tool.  
3. Save the transect assignment file.

### 2.3. Classify Images (Land/Water)

1. Run `app.py` (Land vs Water Classifier).  
2. Load the pre-trained model.  
3. Classifier outputs predictions for selected folder.  
4. Validate and save final classification report (CSV).

### 2.4. Run Preprocessing

1. Run `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`.  
2. Process images per transect assignments.  
3. Fix GPS offsets using external KML files.  
4. Cropped images go into `cropped_images_on_tx`.  
5. Verify correct GPS, coverage, and visible features.

---

## 3. AI-Assisted Object Detection

### 3.1. Change Model Weights (Optional)

1. Select new YOLO `.pt` file.  
2. Replace `best.pt` in `ModelWeights` folder.  
3. Test on a small batch of images.

### 3.2. Edit Otter Checker Config

1. Open Otter Checker config file.  
2. Update image tags/annotation categories.  
3. Test detection output for correct annotation display.

### 3.3. Run SeeOtter Processing

1. Launch `SeeOtter.exe`.  
2. Set `cropped_images_on_tx` as the input directory.  
3. Run the processing pipeline and check output folder for detection results.

### 3.4. Prediction Validation

1. Review bounding boxes, confidence scores.  
2. Mark detections: **Correct**, **Incorrect**, or **Ambiguous**.  
3. Save validation by appending statuses to the annotation file.

### 3.5. Final Processing

1. Run `SeeOtter_post_pro_count_and_split_odd_even.py`.  
2. **Cleanup**: Remove invalid/incomplete detections.  
3. **Validation**: Ensure all detections are classified.  
4. **Count**: Generate the final sea otter population count.  
5. **Effort**: Report images processed, time per transect.  
6. **Geospatial**: Output a shapefile of validated locations.  
7. Verify CSV/shapefile, counts, and coverage.
