import os
import io
import cv2
import time
import numpy as np
import requests
import json
import re
import constants
import PIL.Image as Image
from app import app
from datetime import datetime
from .firebase_storage import get_storage
from .image_processing import process
from redis import Redis
from rq import Queue, Retry

q = Queue(connection=Redis(host='0.0.0.0', port=6379))
storage = get_storage()


def process_order_details_data(order_details_obj):
    order_details = []
    total = 0

    for order in order_details_obj['order-details']:
        order_details.append({
            'product_id': 'string',
            'product_name': order['itemName'],
            'total_amount': int(re.sub('[^0-9]', '', order['total'])),
            'is_addition': True,
            'item_quantity': int(re.sub('[^0-9]', '', order['quantity'])),
            'quantity': int(re.sub('[^0-9]', '', order['quantity'])),
            'unit_price': int(re.sub('[^0-9]', '', order['price'])),
            'discount': 0,
            'final_amount': 0,
            'detail_description': order['annotation'] if 'annotation' in order else 'string',
        })

        total += int(re.sub('[^0-9]', '', order['total']))

    return order_details, total


def save_orders(order_details_obj, img_url):
    is_valid = True

    if len(order_details_obj['order-details']) > 0:
        for order in order_details_obj['order-details']:
            if 'itemName' not in order or 'total' not in order or 'quantity' not in order or 'price' not in order:
                is_valid = False
            else:
                totalStr = re.sub('[^0-9]', '', order['total'])
                quantityStr = re.sub('[^0-9]', '', order['quantity'])
                priceStr = re.sub('[^0-9]', '', order['price'])

                if len(order['itemName'].strip()) == 0 or not isInteger(totalStr) or not isInteger(quantityStr) or not isInteger(priceStr):
                    is_valid = False
    else:
        is_valid = False

    if is_valid:
        order_details, total = process_order_details_data(order_details_obj)
        t = time.localtime()
        current_date = time.strftime('%H:%M:%S', t)

        saved_data = [
            {
                'store_id': 'D_01',
                'rent_code': 'string',
                'invoice_id': 'string',
                'check_in_date': f'{current_date}',
                'check_out_date': f'{current_date}',
                'approve_date': '2020-11-17T18:48:49.852Z',
                'total_amount': total,
                'discount': 0,
                'discount_order_detail': 0,
                'delivery_service_id': 'G',
                'delivery_cost': 0,
                'final_amount': total,
                'delivery_receiver': 'string',
                'delivery_phone': 'string',
                'delivery_address': 'string',
                'delivery_latitude': 0,
                'delivery_longitude': 0,
                'customer_id': 0,
                'order_details': order_details,
                'order_image_urls': [
                    {
                        'image_url': img_url
                    }
                ]
            }
        ]

        with open('access_token.json') as f:
            token = json.load(f)
            access_token = token['access_token']

            r = requests.post(f'{constants.API_DOMAIN}{constants.ORDERS_SAVING_ROUTE}', json=saved_data,
                              headers={'Authorization': 'Bearer ' + access_token})

            if (r.status_code == 201):
                app.logger.info('Save order to database successfully!')
    else:
        app.logger.info('Cannot detect order details from image')


def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def process_img(bytes_str):
    delay = 2
    time.sleep(delay)

    current_time = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')

    try:
        if not os.path.exists('./app/images/'):
            os.makedirs('./app/images/')
    except OSError:
        app.logger.error('Error when creating images directory')

    try:
        # Get image from its bytes string
        img = cv2.imdecode(np.fromstring(
            bytes_str, np.uint8), cv2.IMREAD_COLOR)

        order_details_obj = process(img)

        app.logger.info('Completed to analyze image!')

        img_name = f'bill_{current_time}.png'
        img_path = f'./app/images/{img_name}'

        # Save image to specified path
        Image.open(io.BytesIO(bytes_str)).save(img_path)

        # Uplod image to firebase storage
        storage.child(
            f'images/{img_name}').put(img_path)

        # Get url of image from firebase storage
        img_url = storage.child(f'images/{img_name}').get_url(None)

        save_orders(order_details_obj, img_url)

    except Exception as error:
        raise RuntimeError(error)


def download_and_process_img(record_name, record_path):
    storage.child(
        f'images/{record_name}').download(record_path)

    with open(record_path, 'rb') as record:
        process_img(record.read())
