
Write-Output "[1/4] - Running conda powershell hook"
(& "C:\ProgramData\Anaconda3\Scripts\conda.exe" "shell.powershell" "hook") | Out-String | Invoke-Expression

Write-Output "[2/4] - Activating SeeOtter conda environment"
conda activate "SeeOtter(torch-cpu)"

Write-Output "[3/4] - Building Application"
python -m PyInstaller --noconfirm --clean SeeOtter.spec

Write-Output "[4/4] - Copying Dependencies"
Copy-Item -Path .\yolov5 -Recurse -Destination .\dist\SeeOtter\ -Container

Write-Output "Done!"