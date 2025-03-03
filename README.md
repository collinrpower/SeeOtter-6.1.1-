## Table of Contents

1. [Introduction](#introduction)  
2. [Quick Step-by-Step Instructions](#quick-step-by-step-instructions)  
3. [Comprehensive Workflow Explanation](#comprehensive-workflow-explanation)  
4. [Detailed Installation and Setup Guide](#detailed-installation-and-setup-guide)  
5. [Model Training User Guide (Iterative Active Learning)](#model-training-user-guide-iterative-active-learning)  
6. [Sequential Processing GUI](#sequential-processing-gui)  
7. [Troubleshooting and Support](#troubleshooting-and-support)

---

## Introduction

SeeOtter is a workflow and software suite focused on aerial photography processing and wildlife detection, specifically for sea otter monitoring. It incorporates:

- **YOLOv5**-based object detection  
- **Automated** and **interactive** tools for image backup, annotation, and validation  
- Iterative model training via **active learning**

This README provides:

- Quick start steps  
- Comprehensive instructions  
- Detailed setup information  
- Model training guidelines  
- Full sequential processing workflow  
- Troubleshooting tips and support contacts

---

## Quick Step-by-Step Instructions

### 1. Organize and Backup Data

#### 1.1. Backup Camera Files

**Automated Backup (Preferred)**  
1. Run `Backup_Images.py`.  
2. Specify at least **3 backup drives**.  
3. Choose the destination folders; the script copies images from camera storage to these backups.

**Manual Backup (Alternative)**  
1. Copy raw images to at least 3 physical drives.  
2. Use a structured naming convention, for example:  
   `[Project_Name]_[Survey_Date]_[Camera_ID]_[Location]`  
3. Example directory structure:  
    /Backups/Survey2024/  
        ├── ExternalDrive1/  
        ├── ExternalDrive2/  
        ├── ExternalDrive3/

**Verification**  
- Check file counts/sizes.  
- (Optional) Use checksums (`md5`, `sha256`) to verify integrity.  
- Periodically test backups by accessing them.

---

#### 1.2. Move Image Files into '0' and '1' Camera Folders

**For Non-Waldo Cameras**  
1. Create a directory structure like:  
    /BaseFolder/Location/Camera/Year/MM_DD/  
        ├── 0/  
        ├── 1/  
2. Manually move images or use scripts to place them in the correct folder.

**For Waldo Cameras**  
1. If filename starts with "0", move to folder `0`; if "1", move to folder `1`.  
2. Run `Sort_Waldo_Camera_Images.py` to automate sorting.

**Verification**  
- Open random images in both folders to confirm sorting.  
- Compare timestamps for sequential alignment.  
- Check file counts for any missing images.

---

### 2. Preprocess Images

#### 2.1. Extract Metadata and Verify Quality

1. Run `Image_GPS_extract.py`.  
2. The script outputs a CSV with file path, datetime, latitude/longitude, and altitude.  
3. Inspect the CSV for correctness.  
4. If available, use KML/SHP files for a spatial cross-check.

---

#### 2.2. Assign Images to Transects

1. Use a CSV with columns:
   transect_id, start_img, end_img, start_time, end_time  
2. (Optional) Manually pick start/end images in a map-based tool.  
3. Save the transect assignment file.

---

#### 2.3. Classify Images (Land/Water)

1. Run `app.py` (Land vs Water Classifier).  
2. Load the pre-trained model.  
3. Classifier outputs predictions for selected images.  
4. Validate results and save a final classification CSV.

---

#### 2.4. Run Preprocessing

1. Run `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`.  
2. Process images per transect assignments.  
3. Fix GPS offsets (if using external KML).  
4. Cropped images go to `cropped_images_on_tx`.  
5. Verify GPS corrections, coverage, and image quality.

---

### 3. AI-Assisted Object Detection

#### 3.1. Change Model Weights (Optional)

1. Select new YOLO `.pt` file.  
2. Replace `best.pt` in `ModelWeights` folder.  
3. Test on a small batch of images.

---

#### 3.2. Edit Otter Checker Config

1. Open the Otter Checker config file.  
2. Update image tags/annotation categories to match the new model.  
3. Test to ensure correct annotation display.

---

#### 3.3. Run SeeOtter Processing

1. Launch `SeeOtter.exe`.  
2. Set `cropped_images_on_tx` as the input directory.  
3. Run the processing pipeline; verify detection results in the output folder.

---

#### 3.4. Prediction Validation

1. Review bounding boxes, confidence scores.  
2. Mark detections: **Correct**, **Incorrect**, or **Ambiguous**.  
3. Save these validation results in the annotation file.

---

#### 3.5. Final Processing

1. Run `SeeOtter_post_pro_count_and_split_odd_even.py`.  
2. **Cleanup**: Remove invalid detections.  
3. **Validation**: Confirm all detections are addressed.  
4. **Count**: Generate sea otter population count.  
5. **Effort**: Report survey effort metrics.  
6. **Geospatial**: Output a shapefile of validated locations.  
7. Verify CSV, shapefile, counts, and coverage.

---

## Comprehensive Workflow Explanation

### 1. Organize and Backup Data

#### 1.1. Backup Camera Files

**Importance**
- Protect raw aerial imagery against data loss.
- Retain unaltered originals for future analysis.

**How to Perform**
- **Automated** (`Backup_Images.py`) or **Manual** copy.
- Keep at least three physical backups.
- Use structured naming:
  `[Project_Name]_[Survey_Date]_[Camera_ID]_[Location]`
- Verify file sizes, use checksums, test readability.

---

#### 1.2. Move Image Files into '0' and '1' Camera Folders

**Importance**
- Splitting dual-camera imagery prevents overlap issues.
- Essential for correct transect assignments.

**How to Perform**
- **Non-Waldo**: Manually create `0` and `1` folders.
- **Waldo**: Use `Sort_Waldo_Camera_Images.py` for auto-sorting.

**Verification**
- Random checks on images.
- Confirm timestamps are sequential.
- Check file counts.

---

### 2. Preprocess Images

#### 2.1. Extract Metadata & Verify Data

- Run `Image_GPS_extract.py` to create a CSV with timestamps and GPS.
- Check lat/long, altitudes, and time consistency.
- Compare with KML/SHP if needed.

---

#### 2.2. Assign Images to Transects

- Use a CSV with start/end images or timestamps.  
- Ensure no overlaps/gaps.  
- Save the file.

---

#### 2.3. Classify Images as Land or Water

- Run `app.py` with a deep learning model.  
- Validate uncertain predictions.  
- Only water images proceed.

---

#### 2.4. Run Preprocessing

- Run `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`.  
- Refine GPS data.  
- Cropped images go to `cropped_images_on_tx`.  
- Verify final metadata.

---

### 3. AI-Assisted Object Detection

#### 3.1. Change Model Weights (Optional)

- Replace `best.pt` with a new YOLO `.pt`.  
- Test on a subset before full processing.

---

#### 3.2. Edit Otter Checker Config

- Align config (tags, categories) with the model’s classes.  
- Run a sample detection to confirm annotation display.

---

#### 3.3. Run SeeOtter Processing

- Launch `SeeOtter.exe`.  
- Specify `cropped_images_on_tx` as input.  
- Spot-check final detection outputs.

---

#### 3.4. Prediction Validation

- Examine bounding boxes/confidence scores.  
- Mark correct/incorrect/ambiguous.  
- Save the validation statuses.

---

#### 3.5. Final Processing

- Run `SeeOtter_post_pro_count_and_split_odd_even.py`.  
- Clean data, finalize counts, and produce a shapefile.  
- Confirm coverage and accuracy.

---

## Detailed Installation and Setup Guide

### 1.1. About SeeOtter

- Processes and validates aerial imagery.  
- Utilizes YOLOv5 for object detection.  
- Annotation and validation tools included.

### 1.2. System Requirements

- Windows PC  
- Minimum 8GB RAM (more recommended)  
- Nvidia GPU recommended for performance

### 1.3. Installation Steps

1. **Download**  
   - Obtain SeeOtter from its repository or website.

2. **Extract**  
   - Unzip/copy the SeeOtter folder to a chosen location.

3. **Verify Files**  
   - Must include:
       - `SeeOtter.exe`
       - `see_otter_config.json`
       - `otter_checker_config.json`
       - Supporting folders/files

### 1.4. Initial Setup and Configuration

1. **Launch Application**  
   - Double-click `SeeOtter.exe`.

2. **First-Time Configuration**  
   - Default config files created if missing.
   - Adjust `see_otter_config.json` and `otter_checker_config.json` if needed.

3. **System Check**  
   - Confirm GPU recognition (console output).  
   - Adjust Windows scaling if the UI is cut off.

### 1.5. Troubleshooting & Next Steps

- **Startup Failure**: Check config validity.  
- **Display Issues**: Adjust Windows display settings.  
- Next, create a new survey or refer to model training guides.

---

## Model Training User Guide (Iterative Active Learning)

### 1. Setup and Initialization

- Install SeeOtter on a Windows PC meeting requirements.  
- Launch `SeeOtter.exe`.

### 2. Create a New Survey (Unannotated Dataset)

1. In Survey Manager, click the **+** button.  
2. Fill out:
   - **Survey Name**
   - **Project Path** (existing folder)
   - **Images Path** (defaults to `[ProjectPath/Images]`)
3. Click **Create New Survey**.

### 3. Generate Initial Annotations

1. Open the new survey (`savefile.json`).  
2. Run **Processing** to get predictions.  
3. In **OtterChecker9000**:
   - Mark each detection as Correct, Incorrect, or Ambiguous.
   - Export validated annotations to the **Annotations** folder.

### 4. Train the Initial Model

1. Export validated annotations to form your training dataset.  
2. Split into training/validation sets.  
3. Run training script (e.g., `Train_SeeOtter_Model.py`).  
4. Save model weights (`initial_best.pt`).  
5. Evaluate on the validation set.

### 5. Active Learning Cycle

1. **Run Detection** with the current `.pt` file.  
2. **Review Annotations**; mark newly predicted bounding boxes.  
3. **Update Dataset** with the newly validated annotations.  
4. **Retrain** the model.  
5. **Evaluate** repeatedly until performance is satisfactory.

### 6. Final Evaluation and Deployment

1. Test the final model on a separate test dataset.  
2. Save final weights (e.g., `final_best.pt`).  
3. Update OtterChecker to reference the final model.  
4. Deploy for live detection.

---

## Sequential Processing GUI

### Overview

The **SeeOtter Sequential Processing GUI** offers a clear workflow for aerial imagery surveys, integrating with SeeOtter for wildlife detection.

### Prerequisites

1. **Python 3.8+** with `pandas`, `numpy`, `pillow`, `folium`, `tkinter`.  
2. **Three External Drives** (two archival HDDs, one SSD).  
3. **SeeOtter Scripts** like `Backup_Images.py`, `Image_GPS_extract.py`.

### Installation

1. **Clone/Download** the repository.  
2. **Set Working Directory** in your scripts to the local path.

### Usage Guide

1. **Step 1**: Backup camera files (`Backup_Images.py` or manually).  
2. **Step 2**: Organize images into `0`/`1` folders.  
3. **Step 3**: Extract metadata (`Image_GPS_extract.py`).  
4. **Step 4**: Assign images to transects using CSV.  
5. **Step 5**: Preprocess (`SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`).  
6. **Step 6**: Crop images (reduce vignetting).  
7. **Step 7**: Run `SeeOtter.exe`; validate predictions in OtterChecker9000.  
8. **Step 8**: Final processing (`SeeOtter_post_pro_count_and_split_odd_even.py`).  
9. **Step 9**: Clone filtered surveys for multiple observers if needed.

### Features

- **Step-by-Step Workflow**: Minimizes errors at each stage.  
- **Automated Backups**: Simplifies data preservation.  
- **Metadata Extraction**: Integrates with GIS tools.  
- **Interactive Validation**: OtterChecker9000 annotation checks.  
- **Cloning Surveys**: Enables multi-observer collaboration.

---

## Troubleshooting and Support

**Common Issues**  
- **Script Execution Errors**: Check Python dependencies and file paths.  
- **File Not Found**: Verify folder structures and permissions.  
- **Processing Errors**: Review logs, confirm CSV formatting, ensure prior steps succeeded.  
- **Validation Discrepancies**: Re-check config files; rerun OtterChecker if needed.  
- **GPS Data Missing**: Verify EXIF data or KML file compatibility.

**Support**  
- **Email**: support@wildlifeai.org  
- **Phone**: +1 (800) 123-4567  
- **Website**: [Wildlife AI Support](https://www.wildlifeai.org/support)


# SeeOtter
Sea otter detection application for use in aerial photography surveys.

# Requirements

 - Windows
 - Conda
 - Python 3.9
 - PyTorch
   - https://pytorch.org/get-started/locally/
   - CUDA 11.3 Version Recommended if your computer has a supported Nvidia GPU
     - https://developer.nvidia.com/cuda-11.3.0-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_local
 - Kivy
   - https://kivy.org/doc/stable/gettingstarted/installation.html
   - https://anaconda.org/conda-forge/kivy

---

# Getting Started

Survey acts as the main project file that contains the images and data related to a survey.

## Create

```python
# Create survey with default images dir
survey = Survey.new("SurveyName")
```
```python
# Create survey with existing images dir
survey = Survey.new("SurveyName", images_dir="C:/Path/to/images")
```
```python
# Create survey in different directory
survey = Survey.new("SurveyName", survey_path="C:/Path/to/survey")
```
```python
# Overwrite existing survey
survey = Survey.new("SurveyName", images_dir="C:/Path/to/images", overwrite=True)
```

Creating a new survey will make a survey folder located at:
 
>./Surveys/{SurveyName}

If images_dir is not supplied, an images folder will be created at:

>./Surveys/{SurveyName}/Images

## Load

```python
survey.load("SurveyName")
```

```python
# Reloads images from disk and overwrites all associated data
survey.load("SurveyName", reload_images=True)
```
Load from different directory

```python
survey.load(survey_path="C:/Path/to/survey")
```

## Save

```python
survey.save()
```

---

# Processing

The easiest way to process a survey is to set the current survey in "select_survey.py" and run "main.py"

Add your survey name and image directory to the dict in "select_survey.py"

```python
## select_survey.py
surveys = [
    ("MySurvey1", None),
    ("MySurvey2", "C:/Path/to/images")
]
```

Select the survey you wish to use

```python
## select_survey.py
selected_survey_info = surveys[1]
```

Then run "main.py" to start processing of images.

---

# Waldo Survey

## File Structure

For a Waldo Survey to be imported, it must be stored with the correct naming conventions and folder organization as such:

> DriveLetter:/Location/CameraSystem/YYYY/MM_DD/Waldo Data

Example:

> D:\Cook_Inlet\Waldo\2022\04_11

## Importing/Converting Waldo Survey

>**Note: THE FOLLOWING WILL ALTER THE FILE STRUCTURE AND IMAGE NAMES. DO NOT DO THE FOLLOWING ON ORIGINAL DATA!!**

 - Open the script:

> HelperScripts/create_survey_from_waldo_images.py

 - Set the "image_day" variable to point towards the day of data you want to import (this should end in "MM_DD")
 - Run

This should create a new survey with the name (*Location_YYYY_MM_DD*)

The newly created survey should able to be processed as usual.

# OtterChecker9000

Start by running the script:

> start_otter_checker.py

It will load the survey given by "select_survey.py". Use the red/blue/green buttons to validate the predictions. Click 
the save icon in the top right before exiting to save your progress.

# Deploying Application

To build a deployable application, run the powershell script:

> SeeOtter/Deployment/build_application.ps1

Then copy the folder 'yolov5' to the output folder contining the executable. Failing to do so will give you the following error:

> AttributeError: 'NoneType' object has no attribute 'names'

The executable can be found at:

> SeeOtter\Deployment\dist\SeeOtter\SeeOtter.exe

This uses the python package PyInstaller, and relies on you having the SeeOtter Anaconda environment and Powershell. If 
you have issues running it. Make sure you have the SeeOtter Anaconda environment on your computer, and you're able to 
activate it through Powershell.

> (& "C:\ProgramData\Anaconda3\Scripts\conda.exe" "shell.powershell" "hook") | Out-String | Invoke-Expression

> conda activate SeeOtter


The build settings are defined in the 'SeeOtter.spec' file. Any files or 
directories that need to be included in the application should be listed in this file under the Analysis.datas section 
as such.

    datas=[('../View/Images/*.jpg', 'View/Images'),
           ('../View/Icons/*', 'View/Icons'),
           ('../Surveys', 'Surveys')]

Also, make sure your environment is using Pytorch-cpu when deploying. In theory, it should work with Pytorch-gpu, 
but I haven't had any luck with it. Pyinstaller really doesn't play nicely with cuda. If you have access to the 
SeeOtter(pytorch-cpu) conda environment, then the easiest way is to edit the "build_application.ps1" to point
torwards that environment. 

