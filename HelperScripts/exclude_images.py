from select_survey import load_survey

exclude_images = ["0_000_00_001.jpg"]

survey = load_survey()

has_changes = False
for image_name in exclude_images:
    image = survey.get_image(image_name)
    if image is None:
        print(f"Warning. Could not find image to exclude in survey: '{image_name}'")
        continue
    survey.exclude_image(image)
    has_changes = True

if has_changes:
    survey.save()
    print(survey.description)
else:
    print("No changes made. Skipping project save.")
