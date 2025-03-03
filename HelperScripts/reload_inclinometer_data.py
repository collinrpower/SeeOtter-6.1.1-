from select_survey import load_survey

survey = load_survey()
survey.loaded_inclinometer_files = []
survey.load_and_apply_inclinometer_data()
survey.save()
