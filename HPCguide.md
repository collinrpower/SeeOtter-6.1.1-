# Tallgrass HPC - SeeOtter with YOLOv5 User Guide

This document provides step-by-step instructions for setting up and running SeeOtter with YOLOv5 on Tallgrass HPC, including connecting to the system, preparing the environment, transferring files via Globus, running jobs with SLURM, retrieving processed data, and finalizing annotations.

---

## 1. Connecting to Tallgrass HPC

### 1.1. SSH Login
```
ssh your_username@tallgrass.hpc.url
```

Replace `your_username` with your actual Tallgrass HPC username.


## 2. Loading Required Modules
```
module load python/3.8.5
module load miniconda
module load cuda/11.2
```

## 3. Setting Up the Conda Environment

### 3.1. Create and Activate Environment
```
conda create -n yolov5 python=3.8 -y
conda activate yolov5
```

### 3.2. Install Dependencies
```
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu112
pip install ultralytics globus-sdk
```

### 3.3. Verify GPU Availability
```
python -c "import torch; print(torch.cuda.is_available())"
```

## 4. Organizing Your Project

### 4.1. Directory Structure
```
/projects/SeeOtter/<Project_ID>_<Project_Name>/
├── raw_data/         # Original images and datasets
├── processed_data/   # Processed results
├── models/           # Trained models
├── scripts/          # Python and SLURM scripts
├── logs/             # Job logs and errors
└── docs/             # Project documentation
```

## 5. Transferring Files with Globus

### 5.1. Logging into Globus
1. Visit Globus.org.  
2. Click "Log In" and select your institution.  
3. Authenticate with your credentials.

### 5.2. File Transfer Steps
Select Tallgrass HPC as the destination endpoint.  
Navigate to:
```
/projects/SeeOtter/<Project_ID>_<Project_Name>
```
Upload files:  
- `best.pt` → `/models/`  
- Test images → `/images/` (create if needed)

### 5.3. Verify Transfer
```
ls -l /projects/SeeOtter/<Project_ID>_<Project_Name>/models/
ls -l /projects/SeeOtter/<Project_ID>_<Project_Name>/images/
```

## 6. Running YOLOv5

### 6.1. Submit a Single Job
```
sbatch yolov5_detect.sh
```

### 6.2. Submit a Batch Job
```
sbatch yolov5_detect_batch.sh
```

## 7. Retrieving Processed Data
Log into Globus.org and select Tallgrass HPC as the source endpoint.  
Navigate to:
```
/projects/SeeOtter/<Project_ID>_<Project_Name>/processed_data/
```
Transfer the processed files to your local machine.  
Verify the transfer.

## 8. Example SLURM Scripts

### 8.1. Single Job Script: yolov5_detect.sh
```
#!/bin/bash
#SBATCH --job-name=yolov5_detect
#SBATCH --output=logs/yolov5_detect_%j.out
#SBATCH --error=logs/yolov5_detect_%j.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --mem=4G

module load python/3.8.5
module load miniconda
module load cuda/11.2
source activate yolov5

python detect.py --weights models/best.pt --source images/ --output processed_data/
```

### 8.2. Batch Job Script: yolov5_detect_batch.sh
```
#!/bin/bash
#SBATCH --job-name=yolov5_batch
#SBATCH --output=logs/yolov5_batch_%j.out
#SBATCH --error=logs/yolov5_batch_%j.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --mem=8G

module load python/3.8.5
module load miniconda
module load cuda/11.2
source activate yolov5

for image in images/*.jpg; do
    python detect.py --weights models/best.pt --source "$image" --output processed_data/
done
```

## 9. Finalizing Annotations for SeeOtter
```
python txt2jsonv1.0.py
```
This script:  
- Parses YOLOv5 annotations.  
- Structures predictions for SeeOtter.  
- Generates a JSON file with metadata.  

Verify the JSON before proceeding.

## 10. Additional Resources
- SLURM Quick Start  
- Globus File Transfers  
- Ultralytics YOLOv5  

## 11. Conclusion
This guide outlines the complete workflow for running SeeOtter with YOLOv5 on Tallgrass HPC:  
- Connecting to the system.  
- Preparing your environment.  
- Transferring files.  
- Running and monitoring jobs.  
- Retrieving processed data.  
- Finalizing annotations.  

For issues, consult job logs or contact Tallgrass HPC Support.
