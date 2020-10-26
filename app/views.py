import cv2
import numpy as np
import pprint
from app import app
from flask import request, jsonify
from .image_processing import process

pp = pprint.PrettyPrinter(indent=4)


@app.route('/upload-image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        if request.files:
            # Get image's bytes string
            bytes_str = request.files['image'].read()

            # Get image from its bytes string
            img = cv2.imdecode(np.fromstring(
                bytes_str, np.uint8), cv2.IMREAD_COLOR)

            order_details_obj = process(img)

            # Convert from dictionary object to json
            # response = make_response(jsonify(order_details_obj), 200)
            # pp.pprint(response.get_json())
    message = 'Image is uploaded successfully' if order_details_obj else 'Failed to upload image!'

    return jsonify({'message': message})
