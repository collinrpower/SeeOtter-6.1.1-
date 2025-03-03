from SurveyEntities.survey import Survey
from os.path import exists, join


"""
======================================================================================================
Set currently selected survey to be used for Helper Scripts.

1.  Add new entry to 'surveys' in the format: 
    
    ("SurveyName", "ImagesDir", "SurveyDir")

    Note: ImagesDir and SurveyDir can be set to None. This will set them to their default locations:
        SurveyDir -> SeeOtter/Surveys/[YourSurveyName]
        ImagesDir -> [SurveyDir/Images]

2. Select currently active survey with 'selected_survey_info'

    selected_survey_info = surveys[-1]

3. Run a Helper Script (SeeOtter/HelperScripts) to make things happen
======================================================================================================
"""

#          ("SurveyName", "ImagesDir", "SurveyDir")

surveys = [("KBay_2022", "D:/Otter Surveys/Staging/KBay_Test_2022/Combined"),
           ("Kbay_3cm", "D:/Otter Surveys/Staging/3cm_Kbay/20210318_74941"),
           ("Cook_Inlet_20220411_76886", "D:/Otter Surveys/Staging/Cook_Inlet/Waldo/2022/04_11/20220411_76886"),
           ("Cook_Inlet_2022_04_11", r"C:\Users\ewetherington\Documents\Cook_Inlet\Waldo\2022\04_11\Images"),
           ("TestPaths", "D:\\LoadTest\\Waldo\\2022"),
           (None, None, "C:\\Users\\Evan\\PycharmProjects\\SeeOtter\\Surveys\\TestPaths\\"), # 5
           ("Kbay_2022_Test", None, "D:\\KBay\\Waldo\\2022\\03_29"),
           ("Southeast_2022_05_22", r"D:\Southeast\Waldo\2022\05_22\Images"),
           ("Southeast_2022_05_24", r'I:\Southeast\Waldo\2022\05_24\Images'),
           ("Cook_Inlet_2022_04_11", None, r"F:\Cook_Inlet\Waldo\2022\04_11"),
           ("TestCorruptedImages", None, r"D:\Corrupted_Image_Test\Waldo\2022\04_11"),  # 10
           ("SoutheastSamples_2022_05_22", r"C:\Users\ewetherington\Documents\SoutheastSamples\Waldo\2022\05_22\Images"),
           ("SoutheastSamples_2022_05_27", r"C:\Users\ewetherington\Documents\SoutheastSamples\Waldo\2022\05_27\Images"),
           ("SoutheastSamples_2022_06_05", None, r"D:\SoutheastSamples\Waldo\2022\06_05"),
           ("Cook_Inlet_2022_06_27", None, r"D:\Cook_Inlet\Waldo\2022\06_27"),
           ("Cook_Inlet_2022_06_28", None, r"D:\Cook_Inlet\Waldo\2022\06_28"),
           ("SoutheastSamples_2022_06_17", None, r"F:\SoutheastSamples\Waldo\2022\06_17_test"),
           ("TestImageDirChange", r"F:\SoutheastSamples\Waldo\2022\06_12\Images"),
           ("SoutheastSamples_06_05_akst", None, r"F:\SoutheastSamples\Waldo\2022\06_05_akst"),
           ("TestV2Conversion", None, r"F:\SoutheastSamples\Waldo\2022\05_22_V2"),
           ("SoutheastSamples_06_14_akst", None, r"F:\SoutheastSamples\Waldo\2022\06_14_akst"),
           ("Southeast_2022_05_27_V3_Test", None, r"F:\SoutheastSamples\Waldo\2022\05_27_V3_Test"),
           ("Southeast_2022_05_27_V2_Test", None, r"F:\SoutheastSamples\Waldo\2022\05_27_V2_Test"),
           ("SoutheastSamples_2022_05_31", None, r"F:\SoutheastSamples\Waldo\2022\05_31"),
           ("GLBA_2022_08_04", None, r"D:\GLBA\Waldo\2022\08_04"),
           ("TemporalTesting", None, r"F:\SeeOtterTestSurveys\TemporalTesting"),
           ("Southeast_2022_06_14", r"F:\Southeast\Waldo\2022\06_14\Images"),
           ("Southeast_2022_06_14", None, r"F:\Southeast\Waldo\2022\06_14"),
           (r"F:\SeeOtterTestSurveys\TemporalTesting\savefile.json", None),
           ("TemporalOverlapTest", None, r"F:\SeeOtterTestSurveys\TemporalOverlap"),
           (r"D:\Southeast\Waldo\2022\05_22\savefile.json", r"D:\Southeast\Waldo\2022\05_22\Images"),  # done
           (r"D:\Southeast\Waldo\2022\05_24\savefile.json", r"D:\Southeast\Waldo\2022\05_24\Images"),  # done
           (r"D:\Southeast\Waldo\2022\05_25\savefile.json", r"D:\Southeast\Waldo\2022\05_25\Images"),  # done
           (r"D:\Southeast\Waldo\2022\05_27\savefile.json", r"D:\Southeast\Waldo\2022\05_27\Images"),  # done
           (r"D:\Southeast\Waldo\2022\05_28\savefile.json", r"D:\Southeast\Waldo\2022\05_28\Images"),  # done
           (r"D:\Southeast\Waldo\2022\05_29\savefile.json", r"D:\Southeast\Waldo\2022\05_29\Images"),  # done
           (r"D:\Southeast\Waldo\2022\05_31\savefile.json", r"D:\Southeast\Waldo\2022\05_31\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_01\savefile.json", r"D:\Southeast\Waldo\2022\06_01\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_02\savefile.json", r"D:\Southeast\Waldo\2022\06_02\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_03\savefile.json", r"D:\Southeast\Waldo\2022\06_03\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_05\savefile.json", r"D:\Southeast\Waldo\2022\06_05\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_07\savefile.json", r"D:\Southeast\Waldo\2022\06_07\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_08\savefile.json", r"D:\Southeast\Waldo\2022\06_08\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_09\savefile.json", r"D:\Southeast\Waldo\2022\06_09\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_12\savefile.json", r"D:\Southeast\Waldo\2022\06_12\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_13\savefile.json", r"D:\Southeast\Waldo\2022\06_13\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_14\savefile.json", r"D:\Southeast\Waldo\2022\06_14\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_15\savefile.json", r"D:\Southeast\Waldo\2022\06_15\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_16\savefile.json", r"D:\Southeast\Waldo\2022\06_16\Images"),  # done
           (r"D:\Southeast\Waldo\2022\06_17\savefile.json", r"D:\Southeast\Waldo\2022\06_17\Images"),   # done
           (r"SampleSurvey", None, r"F:\SeeOtterTestSurveys\SampleSurvey"),
           (r"C:\Users\ewetherington\Desktop\MySurvey\savefile.json", None)
           ]

selected_survey_info = surveys[-1]


def get_survey_name():
    return selected_survey_info[0]


def get_survey_image_path():
    return selected_survey_info[1] if len(selected_survey_info) > 1 else None


def get_survey_path():
    return selected_survey_info[2] if len(selected_survey_info) > 2 else None


def load_survey():
    survey_name = get_survey_name()
    survey_image_dir = get_survey_image_path()
    survey_path = get_survey_path()

    if survey_path:
        return Survey.load(survey=survey_path, images_dir=survey_image_dir, reload_images=False)
    if survey_name and exists(join(Survey.get_default_survey_path(survey_name))):
        return Survey.load(survey=survey_name, images_dir=survey_image_dir, reload_images=False)
    if survey_image_dir:
        return Survey.load(survey=survey_image_dir, images_dir=survey_image_dir, reload_images=False)
    else:
        raise Exception(f"Could not find survey given.\nSurvey name: {survey_name}\n"
                        f"Survey path: {survey_path}")
