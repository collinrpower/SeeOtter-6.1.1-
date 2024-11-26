# SeeOtter Sequential Processing GUI

## Overview

The **SeeOtter Sequential Processing GUI** is a comprehensive, step-by-step application designed to guide users through the processing of aerial imagery for wildlife monitoring, specifically sea otters. This guide provides detailed workflows to ensure accurate, efficient, and reliable data processing and validation, integrating seamlessly with the SeeOtter platform.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
  - [Step 1: Backup Camera Files to Hard Drive](#step-1-backup-camera-files-to-hard-drive)
  - [Step 2: Organize Image Files into '0' and '1' Camera Folders](#step-2-organize-image-files-into-0-and-1-camera-folders)
  - [Step 3: Extract Image Metadata and Verify Data Quality](#step-3-extract-image-metadata-and-verify-data-quality)
  - [Step 4: Assign Images to Transects](#step-4-assign-images-to-transects)
  - [Step 5: Run Preprocessing](#step-5-run-preprocessing)
  - [Step 6: Crop Images](#step-6-crop-images)
  - [Step 7: Run SeeOtter Processing and Validate Predictions](#step-7-run-seeotter-processing-and-validate-predictions)
  - [Step 8: Final Processing](#step-8-final-processing)
  - [Step 9: Cloning Filtered Surveys for Multiple Observers](#step-9-cloning-filtered-surveys-for-multiple-observers)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## Prerequisites

Before you begin, ensure the following requirements are met:

1. **Python Environment**:
   - Install Python 3.8 or higher.
   - Install the required Python libraries by running:
     ```bash
     pip install pandas numpy pillow folium tkinter
     ```

2. **Hardware Requirements**:
   - **Three External Drives**:
     - **Two Archival Drives**:
       - Large external hard drives (HDDs) for backups.
       - These drives will serve as archives and will not be processed.
     - **One Working Drive**:
       - A 1-2 TB external solid-state drive (SSD) is recommended.
       - This drive will be used for data processing.
   - **Important**:
     - Do **not** move HDDs while reading or writing data to prevent data loss.

3. **SeeOtter Scripts and Tools**:
   Ensure you have access to the following scripts and executables:
   - `Backup_Images.py`
   - `Move_Waldo_Images_Into_1_0_folders.py`
   - `Image_GPS_extract.py`
   - `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`
   - `SeeOtter_post_pro_count_and_split_odd_even.py`
   - `SeeOtter.exe` (the main executable for SeeOtter)

---

## Installation

1. **Clone or Download the Repository**:
   - Place the application files into a local directory on your machine.

2. **Set the Working Directory**:
   - Modify the working directory in your script to point to your local directory:
     ```python
     os.chdir('E:\\SeeOtterUSGS\\SeeOtter_pre_post-main')
     ```
     Replace `'E:\\SeeOtterUSGS\\SeeOtter_pre_post-main'` with the path to your project directory.

---

## Usage Guide

Follow each step sequentially for accurate data processing.

### Step 1: Backup Camera Files to Hard Drive

**Objective**: Create multiple backups of your raw camera files to prevent data loss.

**Instructions**:

1. **Run `Backup_Images.py` to Automate the Process**:
   - Launch the script.
   - **Select the Number of Backups** you are going to make (at least **three**).
   - **Select the Drive and Folder** where you want the backups placed.
   - **Run the Script**.

2. **Alternatively, Manually Copy and Paste**:
   - Manually copy the camera files onto each backup drive.

**Notes**:

- **Backups should be made on at least 3 separate physical drives**.
- **Two (or more) of these drives** will serve as **archives** and will not be processed.
  - Large external hard drives (HDDs) work well for this purpose.
- **One of these drives** will serve as the **working drive** where the data will be processed.
  - A 1-2 TB external solid-state drive (SSD) is best for the working drive.
  - HDDs will also work but you will see a decrease in performance.
- **Do Not Move HDDs When Reading or Writing Data**.
- After completion, **verify backups** by checking each destination folder to ensure the files have been copied correctly.

---

### Step 2: Organize Image Files into '0' and '1' Camera Folders

**Objective**: Move image files into `0` and `1` camera folders based on which camera the image was taken from.

**Instructions**:

1. **Create a Folder Structure**:
   - Your folder structure should look like this:
     ```
     \*Location*\*Camera*\*YYYY*\*MM_DD*\Images
     ```
     - Example:
       ```
       G:\GBLAtest\Waldo\2022\08_03\Images
       ```

2. **For Non-Waldo Cameras**:
   - **Create an "Images" Folder** in your `MM_DD` folder.
   - **Create Two New Folders** inside the `Images` folder named `0` and `1`.
   - **Copy Images**:
     - Copy all the images from the specific cameras into their respective folders (`0` or `1`).

3. **For Waldo Cameras**:
   - **Run `Move_Waldo_Images_Into_1_0_folders.py`**:
     - Select your `MM_DD` folder when prompted.
     - The script will automatically move the images into the proper `0` and `1` folders.

**Notes**:

- Ensure that the source folders only contain images from the specified cameras.
- The application will create necessary directories if they do not exist.

---

### Step 3: Extract Image Metadata and Verify Data Quality

**Objective**: Extract GPS metadata and timestamps from images and verify data quality.

**Instructions**:

1. **Run `Image_GPS_extract.py`**:
   - A user input window will appear with two options.
   - **For 'Select Input Folder'**:
     - Choose the `Images` folder you created in Step 2.
     - Folder structure should be:
       ```
       X:\*Location*\*Camera*\*YYYY*\*MM_DD*\Images
       ```
       - Example:
         ```
         G:\GBLAtest\Waldo\2022\08_03\Images
         ```
   - **Enter a Name for Your CSV**:
     - Choose the folder where you would like it to be saved.

2. **Verify Data Quality**:
   - Open the CSV you just created to view:
     - Image Filepaths
     - Timestamps
     - Latitudes
     - Longitudes
     - Altitudes
   - Use mapping software (ArcMap, QGIS, Google Earth, etc.) to visualize the data.
   - **Verify**:
     - There are no large gaps with missing data.
     - Images appear to be where they are supposed to be.

3. **Optional**:
   - **Upload a KML or SHP** of the proposed transects to be used as a reference.

**Notes**:

- Ensure that all images have GPS data embedded.
- Missing GPS data may affect subsequent steps.
- Close any CSV files before running the next steps to avoid file overwrite errors.

---

### Step 4: Assign Images to Transects

**Objective**: Assign images to specific transects based on start and end points.

**Instructions**:

1. **Prepare a Transect Assignment CSV**:
   - Use the `tx_assignment_template.csv` or create a CSV with 5 columns:
     ```
     start_img, end_img, transect_id, start_time, end_time
     ```
   - **Fill 'transect_id'** with the names of your proposed transects.

2. **Set Start and End Points for Each Transect**:
   - **Option 1: Using Filepaths**:
     - Fill in the values for `start_img` and `end_img`.
     - Use the full filepath with all forward slashes.
       - Example:
         ```
         G:/GBLAtest/Waldo/2022/08_03/Images/0/20220803_81308_0_000_00_074.jpg
         ```
     - Ensure that `start_img` has a timestamp before `end_img`.
     - This method references the image metadata to identify a time for the start and end images for each transect.
   - **Option 2: Using Timestamps**:
     - Fill in the values for `start_time` and `end_time`.
     - Use this exact format: `YYYY:MM:DD HH:MM:SS`.
     - Ensure that image timestamps and recorded times are in the same timezone.

3. **Important**:
   - **Do Not Fill Out Both Filepaths and Times**:
     - Use one method and leave the other blank.

4. **Verify Transect Assignments**:
   - Use the maps created in previous steps to identify which images are the beginning and end of each transect.
   - Ensure consistency in time zones and formatting.

**Notes**:

- Make sure your transect_assignment.csv is formatted properly:
  - Correct filepaths with forward slashes.
  - Correct timestamp format (`YYYY:MM:DD HH:MM:SS`).
  - Correct capitalization in column headers (lowercase with underscores instead of spaces).

---

### Step 5: Run Preprocessing

**Objective**: Preprocess images, assign them to transects, and correct GPS errors if necessary.

**Instructions**:

1. **Run `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`**:
   - A window will pop up with several options.

2. **Provide Inputs**:
   - **Input Folder**:
     - Select your `Images` folder inside your `MM_DD` folder.
   - **Transect CSV**:
     - Select the `transect_assignment.csv` that was created in Step 4.
   - **Optional KML File**:
     - The KML file is optional to fix GPS errors using a secondary GPS breadcrumb file for the tracklog.
     - Select your KML file if available.
     - **Note**:
       - The KML must have GPS points and associated timestamps.
       - This functionality may not work with all KML formats.

3. **Process KML (If Used)**:
   - With both the CSV and KML selected, run **'Convert KML to CSV'**.
   - This will find the closest point (within 3 seconds) on the KML to the timestamps of your image files and update the image metadata with the alternate GPS locations.

4. **Extract and Assign Transects**:
   - Run **'Extract & Assign Transects'**.
   - This could take a few minutes.
   - This will generate `final_metadata.csv` in your `MM_DD` folder.
     - Contains filepaths, GPS data, and a transect assignment for each image.
   - If you uploaded a KML, this will also generate `final_metadata_updated.csv`.
     - Contains the original image GPS coordinates and the updated coordinates.

5. **Verify Assignments**:
   - Check these CSVs to make sure the transects were assigned properly.
   - Often the first rows will have blank values for the transect assignment column because they were captured in transit to the survey.
   - If transects are not assigned properly:
     - Check your `transect_assignment.csv` for formatting issues.
     - Ensure that your metadata CSVs are closed before running the command again.

**Notes**:

- Common Issues:
  - Incorrect filepaths or time formats.
  - Mismatched time zones.
  - Incorrect capitalization or formatting in CSV headers.
- Ensure that the image metadata CSVs are closed before rerunning the process to avoid overwrite errors.

---

### Step 6: Crop Images

**Objective**: Crop images to improve quality by reducing vignetting effects and prepare them for processing.

**Instructions**:

1. **Set Input Parameters**:
   - **Crop Pixel Size**:
     - Determines how many pixels are cut off from all four edges of each image.
     - **Default**: 125 pixels.
     - This value helps reduce vignetting effects and overlaps between images.
   - **Min Altitude (m)**:
     - Specifies the lowest accepted altitude for images in meters.
     - Everything below this altitude is not processed.
     - **Default**: 152m (~500ft).
   - **Max Altitude (m)**:
     - Specifies the highest accepted altitude for images in meters.
     - Everything above this altitude is not processed.
     - **Default**: 244m (~800ft).

2. **Run 'Crop Images'**:
   - This will:
     - Take every image labeled as on-transect within the specified altitude range.
     - Copy these images into a new folder with an updated naming format compatible with SeeOtter.
     - Crop each side by the specified number of pixels.
     - Correct the image GPS metadata if a KML was used.

3. **Processing Time**:
   - This process could take a few hours.
   - You can ensure that it is still running by navigating to the folder `cropped_images_on_tx` located in your `MM_DD` folder and checking if it is increasing in size.

4. **Verify Cropped Images**:
   - Open the new CSV in your `MM_DD` folder titled `final_metadata_updated_filepath.csv`.
   - Use mapping software to visualize:
     - Image Filepaths
     - Transects
     - Timestamps
     - Latitudes
     - Longitudes
     - Altitudes
   - Verify that there are no large gaps with missing data and images appear to be where they are supposed to be.
   - Select only the points where the column `NewFilepath` is not blank to view the images that were selected as on-transect.

---

### Step 7: Run SeeOtter Processing and Validate Predictions

**Objective**: Process the images using SeeOtter and validate AI predictions.

**Instructions**:

1. **Open `SeeOtter.exe`**:
   - **Note**:
     - The first time `SeeOtter.exe` is opened on a computer, it must be connected to the internet.
     - Once the computer has run SeeOtter, there is no need for internet access in successive runs.

2. **Create a New Survey**:
   - Click the blue plus button in the top left corner of the Survey Manager screen.
   - Fill in the required fields:
     - **Survey Name**: Name of the survey.
     - **Project Path**: Folder that the survey will be created in.
       - Must be an existing folder.
       - Point this to the newly generated `cropped_images_on_tx` folder in your `MM_DD` folder.
     - **Images Path**:
       - Folder containing cropped, on-transect images.
       - Defaults to `[ProjectPath/Images]`.
       - Should be `MM_DD/cropped_images_on_tx/Images`.
       - It's recommended to use the default location to avoid file path issues.

3. **Start Processing**:
   - Press the green play button on the Processing card.
   - Processing includes:
     - Pre-Processing (load and georeference images).
     - Processing (generate predictions).
     - Post-Processing (georeference individuals and generate CSV).
   - **Processing Time**:
     - This process will take a long time depending on how many images your survey contains.
     - Once pre-processing completes, the "Current State" will switch to `RUNNING_IMAGE_DETECTION` and progress will be displayed.
     - This could take 2-4 days running on the computer's CPU.

4. **Validation Settings**:
   - Click on the wrench tool icon in the main screen to access settings.
   - Add initials to **Validator Name** and check the **Validation Mode** checkbox.
   - Select default settings such as starting zoom level.

5. **Validate Predictions in OtterChecker9000**:
   - Navigate to OtterChecker9000 using the button in the top right of the survey manager screen.
   - **Validation Process**:
     - Use the arrows at the top or arrow keys to navigate between images and predictions.
     - The currently selected prediction is marked by a yellow tab above the annotation box.
     - Click an annotation to select it as the current prediction.
     - **Set Min Confidence** to `0.4` and uncheck the **'Show images with no predictions'** box.
     - **Validation Labels**:
       - **Correct (green)**: Prediction is accurate.
       - **Incorrect (red)**: Prediction is not accurate.
       - **Ambiguous (blue)**: Unclear whether the prediction is correct.
     - **Adding Missing Annotations**:
       - Click the pencil icon or press the `D` key to toggle annotation draw mode.
       - Select the appropriate category from the dropdown next to the pencil icon.
         - Default categories:
           - `P` = Pup
           - `O` = Otter
           - `B` = Bird
           - `Sl` = Sea Lion
           - `Porp` = Porpoise
       - Click and drag to draw new annotations.
     - **Save Progress**:
       - Press the save icon in the top right to save the project.
       - A light grey circle will appear around the icon when there are unsaved changes.
       - Save often to avoid losing work.

6. **Secondary Validation (Optional)**:
   - After initial validation, it's good practice to have a second observer review the predictions labeled "CORRECT".
   - **Filters**:
     - Set filters to only show "Correct" and "Unvalidated" predictions above 0.4 confidence.
   - **Process**:
     - Go through the predictions, ensuring there are no unvalidated predictions over the confidence threshold.
     - Double-check each prediction labeled as correct.
     - If the second observer disagrees, mark the prediction as ambiguous.

---

### Step 8: Final Processing

**Objective**: Perform final data processing and prepare results for analysis.

**Instructions**:

1. **Run `SeeOtter_post_pro_count_and_split_odd_even.py`**:
   - This script sums the number of individuals per image and removes image overlap (and potential double counts) by dividing the dataset into odd and even images, creating non-overlapping photo plots.

2. **Outputs**:
   - The final results are a CSV with the following columns:
     - `ImageID`
     - `Datetime`
     - `FilePath`
     - `CameraLatitude`
     - `CameraLongitude`
     - `CameraAltitude`
     - **Counts per Image**:
       - `o count` (otter count per image)
       - `p count` (pup count per image)
       - `o+p count` (combined otter and pup count per image)
       - Counts for any other class you had bounding boxes for by image
     - `transect_id`
     - **Image Corners**:
       - `ImageCorner1Lat`, `ImageCorner1Lon`
       - `ImageCorner2Lat`, `ImageCorner2Lon`
       - `ImageCorner3Lat`, `ImageCorner3Lon`
       - `ImageCorner4Lat`, `ImageCorner4Lon`

3. **Verify Final Results**:
   - Use mapping software to visualize and verify the results.
   - Ensure there are no double counts and data aligns with expectations.

---

### Step 9: Cloning Filtered Surveys for Multiple Observers

**Objective**: Allow multiple observers to validate ambiguous predictions for increased accuracy.

**Instructions**:

1. **Create a Filtered Cloned Survey**:
   - Use the **'Clone Filtered Survey'** feature in SeeOtter.
   - This allows you to create a copy of a survey while filtering by validation type.
   - Select only the "Ambiguous" validations to include.
   - This reduces the file size, making it easier to share.

2. **Share the Cloned Survey**:
   - Distribute the cloned survey to additional observers who have access to SeeOtter.
   - Each validator will need a copy of the survey.

3. **Validation Process**:
   - Validators review the ambiguous predictions.
   - Each validator's input helps resolve uncertainties through majority agreement.

**Notes**:

- It's recommended to have an odd number of validators to avoid ties.
- Ensure that all validators use consistent settings to maintain data integrity.

---

## Features

- **Step-by-Step Workflow**: Guides users through each processing step to ensure accuracy.
- **Automated Backups**: Simplifies the process of creating multiple data backups.
- **Metadata Extraction**: Automatically extracts GPS and timestamp metadata from images.
- **Customizable Validation**: Allows for detailed validation of AI predictions using OtterChecker9000.
- **Cloning Surveys**: Facilitates collaborative validation by creating smaller, manageable survey files.

---

## Troubleshooting

- **Script Execution Errors**:
  - Ensure all required Python dependencies are installed.
  - Verify that all script paths are correctly set in the application.

- **File Not Found**:
  - Check that input folders and files exist and are accessible.
  - Ensure you have the necessary permissions to read/write files.

- **Processing Errors**:
  - Review logs for specific error messages.
  - Check that all previous steps have been completed successfully.
  - Verify the formatting and content of CSV files.

- **Validation Issues**:
  - Ensure that the configuration files are correctly set up.
  - Re-run validation in OtterChecker9000 if discrepancies are found.

- **GPS Data Missing**:
  - Ensure that images have embedded GPS metadata.
  - Verify the KML file format and compatibility if used for GPS correction.

---

## Support

For assistance or to report issues, please contact:

- **Email**: support@wildlifeai.org
- **Phone**: +1 (800) 123-4567
- **Website**: [Wildlife AI Support](https://www.wildlifeai.org/support)

---

*This README was generated to assist users in effectively utilizing the SeeOtter Sequential Processing GUI for wildlife monitoring projects.*
