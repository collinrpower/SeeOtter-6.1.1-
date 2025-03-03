#from DataGenerators.map_generator import MapGenerator
from DataGenerators.kml_map_generator import KmlMapGenerator
from DataGenerators.map_generator import MapGenerator
from DataGenerators.results_generator import ResultsGenerator
from select_survey import load_survey

survey = load_survey()

# Generate Maps
# todo: uncomment and fix map generator
#MapGenerator.survey_map(survey, performance_mode=True).save(survey.map_file_path)
#MapGenerator.survey_otter_map(survey, performance_mode=False).save(survey.otter_map_file_path)
#MapGenerator.survey_transect_map(survey, performance_mode=False).save(survey.transect_map_file_path)
KmlMapGenerator.survey_transect_map(survey, performance_mode=True).save(survey.transect_map_file_path_kml)

# Generate Results
ResultsGenerator(survey).inclinometer_data().save('inclinometer_data.csv')
ResultsGenerator(survey).all_otters().save('results_all_otters.csv')
ResultsGenerator(survey).distinct_otters().save('results_distinct_otters.csv')
ResultsGenerator(survey).all_predictions().save('results_all_predictions.csv')
ResultsGenerator(survey).distinct_otter_count_by_image().save('results_distinct_otter_count_by_image.csv')
ResultsGenerator(survey).validated_predictions().save('validated_predictions.csv')
ResultsGenerator(survey).survey_overview().save('survey_overview.csv')
