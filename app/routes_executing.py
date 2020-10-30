import cv2
import time
import pprint
import numpy as np
from .firebase_storage import get_storage
from .image_processing import process

pp = pprint.PrettyPrinter(indent=4)

storage = get_storage()


def process_img(bytes_str):
    delay = 2
    time.sleep(delay)

    try:
        # Get image from its bytes string
        img = cv2.imdecode(np.fromstring(
            bytes_str, np.uint8), cv2.IMREAD_COLOR)

        order_details_obj = process(img)
        pp.pprint(order_details_obj)
        print('Completed to detect image!')

    except Exception as error:
        raise RuntimeError(error)


def download_and_process_img(record_name, record_path):
    storage.child(
        f'images/{record_name}').download(record_path)

    with open(record_path, 'rb') as record:
        process_img(record.read())
