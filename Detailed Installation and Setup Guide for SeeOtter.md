# Detailed Installation and Setup Guide for SeeOtter

## 1.1. About SeeOtter
- Processes and validates aerial photography.
- Utilizes **YOLOv5** for object detection.
- Provides image validation and annotation tools.

## 1.2. System Requirements
- **Operating System:** Windows PC
- **Memory:** 8GB RAM (or more recommended)
- **GPU:** Nvidia GPU (recommended for faster processing)

## 1.3. Installation Steps

1. **Download**  
   - Obtain the SeeOtter package from the designated repository or website.

2. **Extract**  
   - Unzip or copy the SeeOtter folder to a chosen location on your computer.

3. **Verify Files**  
   - Ensure the folder contains:
     - `SeeOtter.exe` (Main application)
     - `see_otter_config.json` (Processing/runtime settings)
     - `otter_checker_config.json` (Visual/behavior settings)
     - Other supporting files/folders

## 1.4. Initial Setup and Configuration

1. **Launch Application**  
   - Run `SeeOtter.exe` from the SeeOtter folder.

2. **First-Time Configuration**  
   - On first run, default configuration files are created if missing.
   - Check and adjust settings in:
     - `see_otter_config.json`
     - `otter_checker_config.json`

3. **System Check**  
   - Confirm GPU acceleration is enabled (observe console output on startup).
   - Adjust Windows display scaling if the UI appears cut off.

## 1.5. Troubleshooting and Next Steps

### Common Issues
- **Startup Failure:** Verify that configuration files contain valid values.
- **Display Problems:** Right-click Desktop → **Display Settings** to adjust scaling.

### Next Steps
- Refer to the main **SeeOtter User Guide** for a UI walkthrough.
- Create a new survey to start processing images.
- Consult the **Active Learning and Model Training Guide** for model training procedures.
