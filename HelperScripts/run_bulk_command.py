from pathlib import Path

from DataGenerators.kml_map_generator import KmlMapGenerator
from Processing.survey_processing import pre_processing, post_processing, clone_filtered_survey
from SurveyEntities.object_prediction_data import ValidationState
from SurveyEntities.survey import Survey
from Utilities.utilities import print_title

quick_load = True
save_files = [
    # r"D:\Southeast\Waldo\2022\05_22\savefile.json",
    # r"D:\Southeast\Waldo\2022\05_24\savefile.json",
    # r"D:\Southeast\Waldo\2022\05_25\savefile.json",
    # r"D:\Southeast\Waldo\2022\05_27\savefile.json",
    # r"D:\Southeast\Waldo\2022\05_28\savefile.json",
    # r"D:\Southeast\Waldo\2022\05_29\savefile.json",
    # r"D:\Southeast\Waldo\2022\05_31\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_01\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_02\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_03\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_05\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_07\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_08\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_09\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_12\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_13\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_14\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_15\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_16\savefile.json",
    # r"D:\Southeast\Waldo\2022\06_17\savefile.json"

    r"E:\GLBA\Waldo\2022\08_03\savefile.json",
    r"E:\GLBA\Waldo\2022\08_04\savefile.json",
    r"E:\GLBA\Waldo\2022\08_12\savefile.json"

]


###################################################################
# Edit this method
###################################################################
def actions_to_run(survey: Survey):
    include_validation_types = [ValidationState.AMBIGUOUS, ValidationState.CORRECT]
    new_dir_name = str(Path(survey.project_path)) + "(validation)"
    clone_filtered_survey(survey, include_validation_types, out_dir_name=new_dir_name)


###################################################################
# Don't change stuff past here
###################################################################
exit_status = {save_file: "Unprocessed" for save_file in save_files}
for idx, save_file in enumerate(save_files):
    try:
        print_title(f"Processing [{idx+1}/{len(save_files)}]: '{save_file}'")
        survey = Survey.load(save_file, quick_load=quick_load)
        actions_to_run(survey)
        exit_status.update({save_file: "Ran to Completion"})
    except Exception as ex:
        exit_status.update({save_file: f"Error: {ex}"})

print_title("Processing Completed.")
for file, status in exit_status.items():
    print(f"  - Save File: {file}. Status: {status}")
