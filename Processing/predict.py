from os.path import join, exists
from sahi.model import Yolov5DetectionModel
from sahi.predict import get_sliced_prediction, get_prediction
from sahi.utils.yolov5 import download_yolov5s6_model
from tqdm import tqdm

from Config.see_otter_config import SeeOtterConfig
from Utilities.exit_flag import ExitFlag
from Utilities.tqdm_plus import TqdmPlus
from config import *
from Utilities.utilities import get_root_path
from SurveyEntities.survey_image import SurveyImage
from SurveyEntities.survey import Survey


def config() -> SeeOtterConfig:
    return SeeOtterConfig.instance()


"""
Executes predictions for survey images
"""

model_weights_path = join(get_root_path(), MODEL_WEIGHTS_DIR, DEFAULT_MODEL_WEIGHTS_FILE)
if not exists(model_weights_path):
    raise FileNotFoundError(f"Could not locate yolo model weights at [{model_weights_path}]")
download_yolov5s6_model(model_weights_path)
detection_model = Yolov5DetectionModel(
    model_path=model_weights_path,
    confidence_threshold=config().PREDICTION_CONFIDENCE_CUTOFF,
    #device="cpu"
    #device="cuda:0"
)


def run_image_detection(survey: Survey, progress_callback=None, exit_flag: ExitFlag=None):
    slice_images = config().SLICE_PREDICTED_IMAGES
    if survey.num_images == 0:
        print("No images in project. Skipping image prediction.")
        return
    if len(survey.unprocessed_images) == 0:
        print("All images have already been processed. Skipping image prediction.")
        return
    with TqdmPlus(survey.images) as images:
        images.set_description("Running Otter Detection for Images".ljust(PROGRESS_BAR_LABEL_PADDING))
        try:
            autosave_ctr = 0
            for image in images:
                if exit_flag.is_raised:
                    return
                if progress_callback:
                    progress_callback(images)
                if image.has_been_processed:
                    continue
                try:
                    predict_image(image, slice_images=slice_images)
                except MemoryError as me:
                    if slice_images is False:
                        slice_images = True
                        print("Setting 'SLICE_PREDICTED_IMAGES=True' and retrying...")
                        predict_image(image,  slice_images=slice_images)
                    else:
                        raise me
                except ValueError as ve:
                    handle_corrupt_image(survey, image)
                autosave_ctr += 1
                if autosave_ctr >= config().PREDICTION_AUTOSAVE_BATCH_SIZE >= 1:
                    autosave_ctr = 0
                    print("Autosaving, do not close application.")
                    survey.save()

        except Exception as ex:
            print("Error occurred while predicting images. Saving survey before shutdown.")
            survey.save()
            raise ex
        survey.save()
        if config().BACKUP_SURVEY_ON_PREDICTIONS_COMPLETE:
            survey.backup()


def handle_corrupt_image(survey, image):
    print(f"Excluding corrupt image from survey: {image.file_path}")
    survey.exclude_image(image)


def get_sliced_result(image: SurveyImage):
    return get_sliced_prediction(
        image.file_path,
        detection_model,
        slice_height=1024,
        slice_width=1024,
        overlap_height_ratio=0.2,
        overlap_width_ratio=0.2, verbose=0)


def get_result(image: SurveyImage):
    return get_prediction(
        image.file_path,
        detection_model,
        image_size=config().PREDICTION_IMAGE_SIZE,
        verbose=0)


def predict_image(image: SurveyImage, slice_images=config().SLICE_PREDICTED_IMAGES):
    retries = 0
    while True:
        try:
            if slice_images:
                result = get_sliced_result(image)
            else:
                result = get_result(image)
            image.set_prediction_results(result)
            break
        except RuntimeError as re:
            retries += 1
            is_cuda_memory_error = str(re).__contains__("CUDA out of memory")
            cuda_memory_error_message = "CUDA out of memory. Try setting 'SLICE_PREDICTED_IMAGES=True' in the " \
                                        "config. If this does not solve the issue, it may be because your GPU may " \
                                        "not have enough VRAM to perform image predictions."
            if retries > config().MAX_PREDICTION_RETRIES:
                if is_cuda_memory_error:
                    raise MemoryError(cuda_memory_error_message)
                raise re
            elif is_cuda_memory_error:
                print(cuda_memory_error_message)
        except ValueError as ve:
            print(f"Error occurred during image prediction for image: {image.file_path}. This is likely due to a "
                  f"corrupted image. \nError: {ve}")
            raise ve
        except Exception as ex:
            retries += 1
            if retries > config().MAX_PREDICTION_RETRIES:
                raise ex
            print(str(ex))

        print(f"Error occurred during image prediction for image: {image.file_path}. "
              f"Retry: ({retries}/{config().MAX_PREDICTION_RETRIES})")
