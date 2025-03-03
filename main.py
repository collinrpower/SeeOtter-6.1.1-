from DataGenerators.map_generator import MapGenerator
from DataGenerators.results_generator import ResultsGenerator
from Processing.survey_processing import *
from select_survey import *
from Utilities.utilities import print_title
from Processing.predict import run_image_detection


# Create/Load Survey
print_title("LOADING SURVEY")
survey = load_survey()

# Pre-Processing
print_title("PRE-PROCESSING")
pre_processing(survey)

# Predict
print_title("RUN IMAGE DETECTION")
run_image_detection(survey)

# Post-Processing
print_title("POST-PROCESSING")
post_processing(survey)
survey.save()

# Generate Maps
print_title("GENERATE MAPS")
#MapGenerator.survey_map(survey, performance_mode=True).save(survey.map_file_path)
#MapGenerator.survey_otter_map(survey, performance_mode=True).save(survey.otter_map_file_path)
MapGenerator.survey_transect_map(survey, performance_mode=False).save("survey_transect_map.html")

# Generate Results
print_title("GENERATE RESULTS")
ResultsGenerator(survey).all_otters().save('results_all_otters.csv')
ResultsGenerator(survey).distinct_otters().save('results_distinct_otters.csv')
ResultsGenerator(survey).all_predictions().save('results_all_predictions.csv')
ResultsGenerator(survey).distinct_otter_count_by_image().save('results_distinct_otter_count_by_image.csv')
ResultsGenerator(survey).survey_overview().save('survey_overview.csv')

print_title("DONE")
