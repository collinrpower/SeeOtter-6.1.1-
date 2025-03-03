from Utilities.utilities import print_title
from select_survey import load_survey

# todo: finish this
survey = load_survey()

on_transect_images = [image for image in survey.images if image.transect_id is not None]
print(f"On Transect: [{len(on_transect_images)}/{len(survey.images)}]")
