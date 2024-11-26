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
  - [Step 6: Crop Images](#step-6-crop-images)
  - [Step 7: Change Model Weights](#step-7-change-model-weights)
  - [Step 8: Run SeeOtter Processing](#step-8-run-seeotter-processing)
  - [Step 9: Final Processing](#step-9-final-processing)
  - [Cloning Filtered Surveys](#cloning-filtered-surveys)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## Prerequisites

Before you begin, ensure you have met the following requirements:

1. **Python Environment**: Install Python 3.8 or higher.
2. **Required Python Libraries**: Install the necessary Python libraries using:
   ```bash
   pip install pandas numpy pillow folium tkinter
   ```
3. **SeeOtter Scripts and Tools**:
   - `Backup_Images.py`
   - `Move_Waldo_Images_Into_1_0_folders.py`
   - `Image_GPS_extract.py`
   - `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`
   - `SeeOtter_post_pro_count_and_split_odd_even.py`
   - `SeeOtter.exe`
4. **Hardware Requirements**:
   - At least three external drives: two for archival backups (HDDs recommended) and one for processing (SSD preferred).

---

## Installation

1. **Clone or Download the Repository**: Download all necessary files into a local directory.
2. **Set the Working Directory**: Adjust the working directory path in your script:
   ```python
   os.chdir('E:\\SeeOtterUSGS\\SeeOtter_pre_post-main')
   ```
   Replace the path with your directory location.

---

## Usage Guide

### Step 1: Backup Camera Files

**Objective**: Safeguard raw data by creating multiple backups.

**Steps**:
1. Run `Backup_Images.py` or manually copy data.
2. Create **three backups**:
   - **Two archival backups** (HDDs recommended).
   - **One working drive** (SSD preferred for speed).
3. Verify all backups.

**Important**:
- **Do not move HDDs** while reading/writing.
- Check data integrity after copying.

---

### Step 2: Organize Image Files

**Objective**: Separate images into folders for `0` and `1` cameras.

**Steps**:
1. Run `Move_Waldo_Images_Into_1_0_folders.py` for Waldo cameras.
2. Manually create:
   ```
   \*Location*\*Camera*\*YYYY*\*MM_DD*\Images
   ├── 0/
   └── 1/
   ```

---

### Step 3: Extract Image Metadata

**Objective**: Generate metadata with GPS coordinates and timestamps.

**Steps**:
1. Run `Image_GPS_extract.py`:
   - Input: `Images` folder.
   - Output: `original_gps_metadata.csv`.
2. Verify metadata in software like QGIS or ArcMap.

---

### Step 4: Assign Images to Transects

**Objective**: Assign images to transects.

**Steps**:
1. Use `tx_assignment_template.csv` or create:
   ```
   start_img, end_img, transect_id, start_time, end_time
   ```
2. Use **filepaths** or **timestamps**, not both.

---

### Step 5: Run Preprocessing

**Objective**: Preprocess images and assign transects.

**Steps**:
1. Run `SeeOtter_prepro_GUI_non_Waldo_with_GPS_fix.py`.
2. Input:
   - `Images` folder.
   - Transect CSV (`transect_assignment.csv`).
   - Optional: KML for GPS correction.

---

### Step 6: Crop Images

**Objective**: Improve image quality and prepare for analysis.

**Steps**:
1. Run cropping tool.
2. Configure:
   - Crop size: **125 pixels**.
   - Min altitude: **152m**.
   - Max altitude: **244m**.

---

### Step 7: Change Model Weights

**Objective**: Update recognition models.

**Steps**:
1. Replace `best.pt` in `ModelWeights/`.

---

### Step 8: Run SeeOtter Processing

**Objective**: Analyze images and validate predictions.

**Steps**:
1. Launch **SeeOtter.exe**.
2. Create a new survey using the `cropped_images_on_tx` folder.
3. Validate predictions in **OtterChecker9000**.

---

### Step 9: Final Processing

**Objective**: Generate final results by removing overlaps.

**Steps**:
1. Run `SeeOtter_post_pro_count_and_split_odd_even.py`.
2. Outputs:
   - CSV with counts and transect assignments.

---

### Cloning Filtered Surveys

**Objective**: Create smaller surveys for validation.

**Steps**:
1. Use "Clone Filtered Survey" in SeeOtter to share only ambiguous predictions.

---

## Features

- **Automated Processing**: Simplifies workflows.
- **Validation Tools**: Ensure prediction accuracy.
- **Custom Configuration**: Supports diverse survey needs.

---

## Troubleshooting

**Common Issues**:
- Missing GPS data.
- Incorrect filepaths.
- Mismatched timestamps.

---

## Support

**Contact**:
- Email: `support@wildlifeai.org`
- Phone: `+1 (800) 123-4567`
```
