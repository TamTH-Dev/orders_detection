import cv2
import numpy as np
import time
import pprint
from app import app
from flask import request, jsonify
from .image_processing import process
from redis import Redis
from rq import Queue, Retry

pp = pprint.PrettyPrinter(indent=4)

q = Queue(connection=Redis())


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


@app.route('/upload-image', methods=['POST'])
def upload_image():
    q_len = len(q)
    if request.method == 'POST':
        if request.files:
            # Push image's bytes string into queue
            job = q.enqueue(
                process_img, request.files['image'].read(), retry=Retry(max=5))  # Retry 5 times until removed from queue
    return jsonify({'message': 'Image is uploaded successfully!'})
