from tqdm import tqdm

from select_survey import load_survey

survey = load_survey()
print("Reloading image metadata...")
for image in tqdm(survey.images):
    image.reload_metadata()
survey.save()
print("Done")
