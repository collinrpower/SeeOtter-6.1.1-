import shutil
from collections import namedtuple
from time import perf_counter

from SurveyEntities.survey import *
from SurveyEntities.survey_image import *
from Utilities.custom_exceptions import SeeOtterException
from Utilities.image_processing import ImageProcessing
from config import *
from shapely.geometry import Polygon
from Processing.survey_image_processing import *

"""
Processing methods for Survey
"""


def config() -> SeeOtterConfig:
    return SeeOtterConfig.instance()


def pre_processing(survey: Survey, force=False):
    images_to_preprocess = get_images_to_preprocess(survey) if force is False else survey.images
    if can_start_pre_processing(survey, images_to_preprocess):
        calculate_bearing(survey)
        correct_image_orientation(survey, images_to_preprocess)
        set_preprocessed_flag(images_to_preprocess, True)


def post_processing(survey: Survey, skip_already_processed=False):
    calculate_all_predicted_object_coordinates(survey)
    if skip_already_processed:
        not_processed_predictions = [prediction for prediction in survey.predictions if prediction.latitude is 0
                                     and survey.get_image(prediction.image_name).latitude != 0]
        flag_prediction_overlap(survey, include_predictions=not_processed_predictions)
    else:
        flag_prediction_overlap(survey)


def get_images_to_preprocess(survey: Survey):
    return [image for image in survey.images if image.has_been_preprocessed is False]


def can_start_pre_processing(survey: Survey, images_to_preprocess: List[SurveyImage]):
    if survey.has_no_images:
        print("No images in project. Skipping image preprocessing.")
        return False
    elif len(images_to_preprocess) == 0:
        print(f"All {len(survey.images)} images have already been preprocessed. Skipping...")
        return False
    else:
        return True


def correct_image_orientation(survey: Survey, images: List[SurveyImage]):
    with tqdm(images) as images:
        images.set_description(f"Correcting Image Orientation".ljust(PROGRESS_BAR_LABEL_PADDING))
        consecutive_errors = 0
        for image in images:
            try:
                if image.camera.rotate_image:
                    ImageProcessing.rotate_image_to_180(image.file_path)
                    consecutive_errors = 0
            except OSError as ose:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    print("Maximum consecutive errors hit while correcting image orientation.")
                    raise ose
                survey.exclude_image(image)
                print(f"Excluding image ({image.file_name}) due to error during image rotation (file is likely "
                      f"corrupted). Error Message: {ose}")


def calculate_bearing(survey: Survey):
    if survey.has_no_images:
        print("No images in project. Skipping bearing calculation.")
        return
    print("Calculating Direction Heading...")
    for i in range(survey.num_images):
        current = survey.images[i]
        previous = None
        next = None
        if i > 0:
            previous = survey.images[i - 1]
        if i < survey.num_images - 1:
            next = survey.images[i + 1]
        current.direction = calculate_bearing_from_neighbor_images(current, previous, next)


def clear_transect_overlap_flags(survey: Survey):
    [prediction.transect_overlap_images.clear() for prediction in survey.predictions]


def clear_temporal_overlap_flags(survey: Survey):
    for prediction in survey.predictions:
        prediction.overlaps_image = None


def get_grid_dimensions(grid):
    return len(grid), len(grid[0])


def get_images_with_validation_type(survey: Survey, allowed_validation_states: List[ValidationState]):
    images_with_validation_type = []
    for image in survey.images:
        for prediction in image.predictions:
            if prediction.validation_state in allowed_validation_states:
                images_with_validation_type.append(image)
                break
    return images_with_validation_type


def vote_ambiguous_validations(survey: Survey, force_save=False):
    print("Voting ambiguous predictions...")
    dir = survey.get_relative_path(AMBIGUOUS_VOTE_DIR)
    files = [join(dir, file) for file in os.listdir(dir) if file.endswith(".csv")]
    if len(files) == 0:
        raise SeeOtterException(f"Cannot vote ambiguous predictions. No csv files found at '{dir}'")
    if len(files) % 2 == 0:
        raise SeeOtterException(f"Odd number of files required to vote ambiguous predictions")
    file_data = [read_csv_dict_list(file) for file in files]
    for prediction in survey.validated_ambiguous_predictions:
        votes = []
        for file in file_data:
            for row in file:
                try:
                    # Find matching row in csv and add validation state to votes
                    file_name = os.path.basename(row["FilePath"])
                    if prediction.image_name == file_name and int(prediction.xmin) == int(float(row["BoxMinX"])) \
                            and int(prediction.ymin) == int(float(row["BoxMinY"])):
                        validation_state = ValidationState[row["ValidationState"]]
                        votes.append(validation_state)
                        if validation_state in (ValidationState.AMBIGUOUS, ValidationState.UNVALIDATED):
                            print(f"Warning: Incorrect or ambiguous validation found. State: {validation_state}, "
                                  f"File: {file_name}, Validator: {row['ValidatedBy']}")
                except Exception as ex:
                    print(f"Error voting ambiguous for row: {row}")
                    raise ex
        # Count votes and apply changes
        correct_count = votes.count(ValidationState.CORRECT)
        incorrect_count = votes.count(ValidationState.INCORRECT)
        if correct_count > incorrect_count:
            prediction.validation_state = ValidationState.CORRECT
        elif incorrect_count > correct_count:
            prediction.validation_state = ValidationState.INCORRECT
        else:
            if correct_count == 0:
                print("Warning: No predictions found for prediction.")
            else:
                print(f"Warning: Cannot vote on prediction. Same number of correct and incorrect predictions "
                      f"({correct_count}).")
            print(f"Image: {prediction.image_name}, BoxMinX: {prediction.xmin}")
    if force_save or prompt_user("Completed voting of ambiguous validations.\nSave changes? [Y/N]"):
        survey.backup()
        survey.save()


def clone_survey(survey: Survey, new_survey_path, skip_excluded_images=False, force=False):
    """
    Clone a survey and it's files to a new location
    :param survey: Survey to clone
    :param new_survey_path: Dir the cloned survey will be copied to
    :param skip_excluded_images: If true, excluded images will not be copied
    :param force: If true, user will not prompted to overwrite existing dir
    :return: None
    """
    if not paths_equal(Path(survey.images_dir).parent, survey.project_path):
        raise Exception(f"This operation is not currently supported for surveys with an Image dir not in same location "
                        f"as project dir.\n - Image Dir: {survey.images_dir}\n - Project Path: {survey.project_path}")
    if exists(new_survey_path):
        if force or prompt_user(f"Destination path already exists: {new_survey_path}\nOverwrite destination? [Y/N]"):
            shutil.rmtree(new_survey_path)
        else:
            raise Exception("Operation cancelled by user")
    for file in os.listdir(survey.project_path):
        if file == "Images":
            img_dst = join(new_survey_path, "Images")
            os.makedirs(img_dst)
            images_to_copy = survey.images if skip_excluded_images else survey.images + survey.excluded_images
            images_to_copy = tqdm(images_to_copy)
            for image in images_to_copy:
                images_to_copy.set_description("Copying Images")
                shutil.copy2(src=image.file_path, dst=img_dst)
        else:
            src_path = join(survey.project_path, file)
            dst_path = join(new_survey_path, file)
            mkdir_if_not_exists(new_survey_path)
            if os.path.isdir(src_path):
                shutil.copytree(src=src_path, dst=dst_path)
            elif os.path.isfile(src_path):
                shutil.copy2(src=src_path, dst=dst_path)
            else:
                raise Exception(f"Error copying file: {src_path}")


def clone_filtered_survey(survey: Survey, include_validation_types: List[ValidationState], out_dir_path=None,
                          out_dir_name=None, force=False):
    """
    Filters out images and predictions not matching the given types and creates a clone of the
    survey with unused images being excluded.
    :param force: Overwrites existing files without prompt
    :param survey: Survey
    :param include_validation_types: Allowed validation state types
    :param out_dir_path: Path for cloned survey (ignore if out_dir_name is specified)
    :param out_dir_name: If specified, will create a new directory with this name in the same parent dir as the given
     survey (ignore if out_dir_path is specified)
    """
    if out_dir_path is None:
        if out_dir_name is None:
            raise Exception("Must supply one of the following arguments: 'out_dir_name', 'out_dir_path'")
        parent_path = Path(survey.project_path).parent
        out_dir_path = os.path.join(parent_path, out_dir_name)

    survey_copy = copy.deepcopy(survey)
    survey_copy.excluded_images.clear()

    keep_images = get_images_with_validation_type(survey_copy, include_validation_types)
    remove_images = [image for image in survey_copy.images if image not in keep_images]

    for image in remove_images:
        survey_copy.images.remove(image)

    for image in keep_images:
        image.predictions = [pred for pred in image.predictions if pred.validation_state in include_validation_types]

    clone_survey(survey_copy, out_dir_path, skip_excluded_images=True, force=force)
    survey_copy.update_paths(project_path=out_dir_path, images_dir=join(out_dir_path, "Images"))
    survey_copy.save()
    return Survey.get_survey_save_file_path(out_dir_path)


def flag_prediction_overlap(survey: Survey, include_predictions=None):
    print("Flagging prediction overlap...")
    clear_transect_overlap_flags(survey)
    clear_temporal_overlap_flags(survey)
    grid = get_image_coordinate_grid(survey)
    progress_bar = tqdm(total=survey.num_images)
    progress_bar.set_description(f"Flagging prediction overlap".ljust(PROGRESS_BAR_LABEL_PADDING))
    for row_id, row in enumerate(grid):
        for col_id, cell in enumerate(row):
            cell_images = [image for image in cell]
            if len(cell_images) == 0:
                continue
            neighbor_cells = get_local_image_coordinate_cells(grid, row_id, col_id)
            nearby_images = get_images_from_image_coordinate_cells(neighbor_cells)
            for image in cell_images:
                progress_bar.update()
                if not image or len(image.predictions) == 0:
                    continue
                if include_predictions is not None:
                    predictions = [p for p in image.predictions if include_predictions.__contains__(p)]
                else:
                    predictions = image.predictions
                if len(predictions) == 0:
                    continue
                for nearby_image in nearby_images:
                    if nearby_image == image:
                        continue
                    poly = geometry.Polygon(get_coordinate_bounds(nearby_image))
                    overlapping_predictions = Survey.get_predictions_within_polygon(poly, predictions)
                    for prediction in overlapping_predictions:
                        if Survey.are_consecutive_images(image, nearby_image):
                            prediction.overlaps_image = nearby_image.file_name
                        else:
                            if prediction.transect_overlap_images.__contains__(nearby_image.file_name):
                                print(f"{len(prediction.transect_overlap_images)} Nearby images: "
                                      f"{prediction.transect_overlap_images}")
                            prediction.add_transect_overlap_image(nearby_image.file_name)


def get_image_coordinate_grid(survey: Survey):
    min_coords, max_coords = survey.get_min_max_coordinate_bounds()
    lat_range = max_coords[0] - min_coords[0]
    lon_range = max_coords[1] - min_coords[1]
    grid_rows = int(lat_range / config().IMAGE_COORDINATE_CHUNKING_DEGREES_LAT) + 1
    grid_cols = int(lon_range / config().IMAGE_COORDINATE_CHUNKING_DEGREES_LON) + 1
    coordinate_grid = [[[] for i in range(grid_cols)] for j in range(grid_rows)]
    for image in survey.images:
        if image.latitude != 0 and image.longitude != 0:
            lat_offset = image.latitude - min_coords[0]
            lon_offset = image.longitude - min_coords[1]
            lat_index = int(lat_offset / config().IMAGE_COORDINATE_CHUNKING_DEGREES_LAT)
            lon_index = int(lon_offset / config().IMAGE_COORDINATE_CHUNKING_DEGREES_LON)
            coordinate_grid[lat_index][lon_index].append(image)

    return coordinate_grid


def try_get_grid_cell(grid, lat_index, lon_index):
    grid_height = len(grid)
    grid_width = len(grid[0])
    valid_lat = 0 <= lat_index < grid_height
    valid_lon = 0 <= lon_index < grid_width
    if valid_lat and valid_lon:
        return grid[lat_index][lon_index]

    return None


def get_local_image_coordinate_cells(grid, lat_index, lon_index):
    grid_width, grid_height = len(grid[0]), len(grid)
    min_lat = max(0, lat_index - 1)
    max_lat = min(grid_height - 1, lat_index + 1)
    min_lon = max(0, lon_index - 1)
    max_lon = min(grid_width - 1, lon_index + 1)
    cells = [cell for row in grid[min_lat:max_lat + 1] for cell in row[min_lon:max_lon + 1]]

    return cells


def get_images_from_image_coordinate_cells(cells):
    return [image for cell in cells for image in cell]


def get_distinct_predictions_for_image(image: SurveyImage, survey: Survey):
    distinct_predictions = [image for image in image.predictions]
    for prediction in image.predictions:
        overlap_images = [prediction.overlaps_image]
        overlap_images += prediction.transect_overlap_images
        remove_empty_elements(overlap_images)
        overlap_images = [survey.get_image(image_name) for image_name in overlap_images]
        for overlap_image in overlap_images:
            if overlap_image.datetime > image.datetime:
                distinct_predictions.remove(prediction)
                break
    return distinct_predictions


def get_distinct_predictions(survey: Survey):
    """
    Gets distinct predictions by ignoring predictions located in the same area
    as newer images.
    :param survey: Survey
    :return: List of distinct predictions
    """
    distinct_predictions = []
    for idx, image in enumerate(survey.images):
        distinct_predictions += get_distinct_predictions_for_image(image, survey)
    return distinct_predictions


def get_distinct_filtered_predictions(survey,
                                      confidence_cutoff=RESULTS_CONFIDENCE_CUTOFF,
                                      category_name=config().OTTER_CATEGORY_NAME):
    distinct = get_distinct_predictions(survey)
    return get_distinct_filtered_predictions(distinct, confidence_cutoff, category_name)


def filter_predictions(predictions: List[ObjectPredictionData],
                       confidence_cutoff=RESULTS_CONFIDENCE_CUTOFF,
                       category_name=config().OTTER_CATEGORY_NAME):
    return [prediction for prediction in predictions
            if prediction.score >= confidence_cutoff
            and (prediction.category_name == category_name or prediction.category_name == 'p')
            and prediction.validation_state == 1]


def get_images_within_radius(survey, image: SurveyImage, meters, images=None):
    images_within_radius = []
    images = images or survey.images
    for other_image in images:
        distance = get_distance_between_images(image, other_image)
        if 20 <= distance <= meters:
            images_within_radius.append(other_image)

    return images_within_radius


def get_unvalidated_predictions(survey: Survey):
    return [prediction for prediction in survey.predictions
            if prediction.validation_state == ValidationState.UNVALIDATED]


def set_preprocessed_flag(images: List[SurveyImage], flag=True):
    for image in images:
        image.has_been_preprocessed = flag


def calculate_all_predicted_object_coordinates(survey: Survey):
    print("Calculating predicted object coordinates...")
    with tqdm(survey.images) as images:
        images.set_description(f"Calculating predicted object coordinates".ljust(PROGRESS_BAR_LABEL_PADDING))
        [calculate_predicted_object_coordinates(image) for image in images]
