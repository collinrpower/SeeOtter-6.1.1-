# SeeOtter-6.1.1-
# SeeOtter Sequential Processing GUI

## Overview

The **SeeOtter Sequential Processing GUI** is a step-by-step application designed to guide users through the processing of aerial imagery for wildlife monitoring, specifically sea otters. This GUI simplifies complex workflows, ensures data integrity, and integrates seamlessly with the SeeOtter platform.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
  - [Step 1: Backup Camera Files](#step-1-backup-camera-files)
  - [Step 2: Organize Image Files](#step-2-organize-image-files)
  - [Step 3: Extract Image Metadata](#step-3-extract-image-metadata)
  - [Step 4: Assign Images to Transects](#step-4-assign-images-to-transects)
  - [Step 5: Run Preprocessing](#step-5-run-preprocessing)
  - [Step 6: Change Model Weights](#step-6-change-model-weights)
  - [Step 7: Edit Otter Checker Config](#step-7-edit-otter-checker-config)
  - [Step 8: Run SeeOtter Processing](#step-8-run-seeotter-processing)
  - [Step 9: Final Processing](#step-9-final-processing)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## Prerequisites

Before you begin, ensure you have met the following requirements:

1. **Python Environment**: Install Python 3.8 or higher.
2. **Required Python Libraries**: Install the necessary Python libraries using the following command:
   ```bash
   pip install pandas numpy pillow folium tkinter
   ```
3. **SeeOtter Scripts and Tools**: Ensure you have access to the following scripts and executables:
   - `Backup_Images.py`
   - `Image_GPS_extract.py`
   - `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`
   - `SeeOtter_post_pro_count_and_split_odd_even.py`
   - `SeeOtter.exe` (the main executable for SeeOtter)
4. **Folder Structure**: Set up your project directory with the following subdirectories:
   - `ModelWeights/` (to store model weight files)
   - `Config/` (to store configuration files)

---

## Installation

1. **Clone or Download the Repository**: Place the application files into a local directory on your machine.
2. **Set the Working Directory**: Modify the working directory in the code to point to your local directory:
   ```python
   os.chdir('E:\\SeeOtterUSGS\\SeeOtter_pre_post-main')
   ```
   Replace `'E:\\SeeOtterUSGS\\SeeOtter_pre_post-main'` with the path to your project directory.

---

## Usage Guide

The application guides you through nine sequential steps. Each step is crucial for the accurate processing of imagery data.

### Step 1: Backup Camera Files

**Objective**: Create multiple backups of your raw camera files to prevent data loss.

**What You Need**:
- The folder containing the raw images from your cameras.
- At least three different destination folders on separate physical drives for backups.

**Instructions**:

1. **Launch the Application** and proceed to Step 1.
2. **Select the Source Folder**:
   - Click the **Browse** button next to "Select Folder to Backup".
   - Navigate to the folder containing your camera files and select it.
3. **Add Destination Folders**:
   - Click the **Add Destination** button.
   - For each backup, select a different destination folder on a separate physical drive.
   - Repeat this process to add at least three destination folders.
4. **Start Backup**:
   - Click the **Start Backup** button.
   - The application will copy the files from the source folder to each of the destination folders.
5. **Verify Backups**:
   - After completion, check each destination folder to ensure the files have been copied correctly.

**Notes**:
- Backing up on multiple drives prevents data loss due to hardware failure.
- Ensure you have sufficient storage space on each backup drive.

### Step 2: Organize Image Files

**Objective**: Organize your images into `0` and `1` camera folders based on which camera captured the image.

**What You Need**:
- The backed-up images from Step 1.
- Information about the camera type (Waldo or Generic).
- Details for folder naming (Location, Camera Number, Year, MM_DD).

**Instructions**:

1. **Select Camera Type**:
   - Choose between **Waldo Camera** and **Generic Camera** based on the equipment used.
2. **Fill in Required Details**:
   - **Location**: Enter the survey location name.
   - **Camera Number**: Enter the camera identifier (e.g., `0` or `1`).
   - **Year**: Enter the year of the survey (e.g., `2023`).
   - **MM_DD**: Enter the month and day (e.g., `07_15` for July 15th).
3. **Select Source Folders**:
   - For **Generic Camera**:
     - Click **Add Source Folder** for each camera used.
     - Select the folder containing images for each camera.
   - For **Waldo Camera**:
     - Click the **Browse** button next to "Select Source Folder".
     - Choose the folder containing all images.
4. **Specify Base Folder**:
   - Click the **Browse** button next to "Base Folder".
   - Select the main directory where you want to organize your images.
5. **Move Images**:
   - Click **Move Generic Images** or **Move Waldo Images** depending on your camera type.
   - The application will organize images into `0` and `1` folders within the specified directory structure.

**Resulting Folder Structure**:
```
Base Folder/
└── Location/
    └── Camera/
        └── Year/
            └── MM_DD/
                ├── 0/ (Images from camera 0)
                └── 1/ (Images from camera 1)
```

**Notes**:
- Ensure that the source folders only contain images from the specified cameras.
- The application will create necessary directories if they do not exist.

### Step 3: Extract Image Metadata

**Objective**: Extract GPS metadata and timestamps from images and verify data quality.

**What You Need**:
- The organized images from Step 2.
- A destination path for the output CSV file.

**Instructions**:

1. **Select Input Folder**:
   - Click the **Browse** button next to "Input Folder".
   - Choose the `MM_DD` folder created in Step 2.
2. **Specify Output CSV**:
   - The application automatically suggests `original_gps_metadata.csv` in the same directory.
   - You can change the path if desired.
3. **Extract Metadata**:
   - Click **Extract Metadata**.
   - The application runs `Image_GPS_extract.py` to extract metadata.
4. **Verify Data Quality**:
   - Open the generated CSV file.
   - Check the columns for `Filepath`, `DatetimeOriginal`, `Latitude`, `Longitude`, and `Altitude`.
5. **Optional**:
   - Upload a KML or SHP file of the proposed transects for reference.

**Notes**:
- Ensure that all images have GPS data embedded.
- Missing GPS data may affect subsequent steps.

### Step 4: Assign Images to Transects

**Objective**: Assign images to specific transects based on start and end points.

**What You Need**:
- The `original_gps_metadata.csv` file from Step 3.
- A CSV template or existing transect assignment CSV.

**Instructions**:

1. **Load or Create CSV**:
   - Click **Load CSV** to use an existing transect assignment file.
   - Or click **Create Default CSV** to generate a new template.
2. **Define Transects**:
   - For each transect, fill in the following fields:
     - **start_img**: The file path or timestamp of the first image in the transect.
     - **end_img**: The file path or timestamp of the last image in the transect.
     - **transect_id**: A unique identifier for the transect.
     - **start_time**: The timestamp of the start image (if not using file paths).
     - **end_time**: The timestamp of the end image (if not using file paths).
3. **Add Rows**:
   - Click **Add Row** to include more transects.
4. **Save CSV**:
   - Click **Save CSV**.
   - The default save location is within the `MM_DD` folder as `transect_assignment.csv`.

**Notes**:
- Ensure that the start and end images accurately represent the transect boundaries.
- Use consistent formatting for timestamps and file paths.

### Step 5: Run Preprocessing

**Objective**: Preprocess images and assign them to transects.

**What You Need**:
- The `Images` folder inside your `MM_DD` directory.
- The `transect_assignment.csv` from Step 4.
- (Optional) A KML file for GPS correction.

**Instructions**:

1. **Run Preprocessing Script**:
   - Click **Run Preprocessing**.
   - The application will execute `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`.
2. **Provide Inputs**:
   - **Input Folder**: Select your `Images` folder.
   - **Transect CSV**: Select the `transect_assignment.csv` file.
   - **KML File**: (Optional) Select a KML file for GPS correction.
3. **Execute Extraction**:
   - Click **Extract & Assign Transects** within the preprocessing GUI.
4. **Monitor Progress**:
   - The script will process images and organize them according to transects.

**Notes**:
- Ensure all input paths are correct to avoid processing errors.
- The preprocessing may take some time depending on the number of images.

### Step 6: Change Model Weights

**Objective**: Update the model weights used for image recognition.

**What You Need**:
- A new `.pt` file containing the updated model weights.
- Access to the `ModelWeights` directory.

**Instructions**:

1. **Select New Model Weights**:
   - Click **Change Model Weights**.
   - Browse and select the new `.pt` file.
2. **Backup Existing Weights**:
   - The application will automatically create a backup of the current `best.pt` file.
   - The backup is saved with a timestamp in the `ModelWeights` folder.
3. **Replace Weights**:
   - The selected new weights file will replace the existing `best.pt` file.
4. **Confirm Update**:
   - A success message will confirm the weights have been updated.

**Notes**:
- Always keep backups of model weights for reproducibility.
- Ensure the new weights are compatible with your version of SeeOtter.

### Step 7: Edit Otter Checker Config

**Objective**: Customize the configuration for image tagging and annotation categories.

**What You Need**:
- Access to the `Config/otter_checker_config.py` file.
- Knowledge of the desired image tags and annotation categories.

**Instructions**:

1. **Load Current Config**:
   - The application will display the current `IMAGE_TAGS` and `ANNOTATION_CATEGORIES`.
2. **Modify Image Tags**:
   - Edit the tags in the provided text fields.
   - These tags are used for labeling images during analysis.
3. **Modify Annotation Categories**:
   - Edit the categories and their corresponding indices.
   - Click **Add Category** to include additional categories.
4. **Save Config**:
   - Click **Save Config**.
   - A backup of the existing config file will be created.
5. **Restart Application**:
   - Changes will take effect upon restarting the SeeOtter application.

**Notes**:
- Ensure that category indices are unique and correctly assigned.
- Incorrect configurations may lead to processing errors.

### Step 8: Run SeeOtter Processing

**Objective**: Process the images using SeeOtter and validate predictions.

**What You Need**:
- The `cropped_images_on_tx` folder generated from preprocessing.
- Access to `SeeOtter.exe`.

**Instructions**:

1. **Start SeeOtter**:
   - Click **Start SeeOtter**.
   - The application will run `start_see_otter_no_survey.py` to launch SeeOtter.
2. **Create New Survey**:
   - Within SeeOtter, select **Create New Survey**.
3. **Select Images Folder**:
   - Point to the `cropped_images_on_tx` folder.
4. **Begin Processing**:
   - Start the survey processing within SeeOtter.
   - Monitor the progress and wait for completion.
5. **Validate Predictions**:
   - Use **OtterChecker9000** to review and validate the AI predictions.
   - Correct any misclassifications or anomalies.

**Notes**:
- Ensure that SeeOtter is properly installed and licensed.
- Validation is crucial for data accuracy.

### Step 9: Final Processing

**Objective**: Perform final data processing and prepare results for analysis.

**What You Need**:
- The processed data from SeeOtter.
- Access to `SeeOtter_post_pro_count_and_split_odd_even.py`.

**Instructions**:

1. **Run Final Processing Script**:
   - Click **Run Final Processing**.
   - The application will execute the final processing script.
2. **Verify Results**:
   - After processing, review the output files.
   - Use mapping software to visualize and verify the results.
3. **Split Data**:
   - The script may split data into odd and even sets for statistical analysis.
4. **Finalize Data**:
   - Prepare the data for reporting or further analysis.

**Notes**:
- Ensure that all previous steps have been completed successfully.
- Keep backups of all output data.

---

## Features

- **Interactive GUI**: User-friendly interface to guide through each processing step.
- **Automated Backups**: Easily create multiple backups to prevent data loss.
- **Metadata Extraction**: Automatically extract and compile GPS metadata from images.
- **Customizable Configuration**: Edit image tags and categories to suit your project needs.
- **Seamless Integration**: Works in conjunction with SeeOtter and OtterChecker9000 for efficient workflow.

---

## Troubleshooting

- **Script Execution Errors**:
  - Ensure all required Python dependencies are installed.
  - Check that all script paths are correctly set in the application.
- **File Not Found**:
  - Verify that input folders and files exist and are accessible.
  - Ensure you have the necessary permissions to read/write files.
- **Processing Errors**:
  - Review logs for specific error messages.
  - Check that all previous steps have been completed successfully.
- **Validation Issues**:
  - Ensure that the configuration files are correctly set up.
  - Re-run validation in OtterChecker9000 if discrepancies are found.

---

## Support

For assistance or to report issues, please contact:

- **Email**: support@wildlifeai.org
- **Phone**: +1 (800) 123-4567
- **Website**: [Wildlife AI Support](https://www.wildlifeai.org/support)

---

*This README was generated to assist users in effectively utilizing the SeeOtter Sequential Processing GUI for wildlife monitoring projects.*
