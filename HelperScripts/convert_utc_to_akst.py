import os
from os.path import join
from tqdm import tqdm
from Utilities.image_processing import ImageProcessing

'''
*** NOTE: Must run 'reload_image_metadata.py' for changes to be applied to survey *** 
'''

image_dir = r"F:\SeeOtterTestSurveys\TemporalTesting\Images"

images = [join(image_dir, file) for file in os.listdir(image_dir) if file.lower().endswith(".jpg")]
response = input(f"You are about to convert {len(images)} images datetime from UTC to AKST in the folder "
                 f"'{image_dir}'. If the images are not currently using UTC time, this will cause incorrect time to "
                 f"be set!!! \n *** To continue, type 'aardvark' ***")
if response == "aardvark":
    print("Beginning conversion.")
    for image in tqdm(images):
        ImageProcessing.update_utc_image_time(path=image, force=True)
else:
    print("Operation Cancelled.")
