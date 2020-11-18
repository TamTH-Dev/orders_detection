import cv2
import time
import numpy as np
import requests
import json
import re
import constants
from .firebase_storage import get_storage
from .image_processing import process
from redis import Redis
from rq import Queue, Retry

q = Queue(connection=Redis(host='0.0.0.0', port=6379))
storage = get_storage()


def process_order_details_data(order_details_obj):
    order_details = []

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

    return order_details


def save_orders(order_details_obj):
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
        t = time.localtime()
        current_time = time.strftime('%H:%M:%S', t)

        saved_data = [
            {
                'store_id': 'D_01',
                'rent_code': 'string',
                'invoice_id': 'string',
                'check_in_date': f'{current_time}',
                'check_out_date': f'{current_time}',
                'approve_date': '2020-11-17T18:48:49.852Z',
                'total_amount': 0,
                'discount': 0,
                'discount_order_detail': 0,
                'delivery_service_id': 'G',
                'delivery_cost': 0,
                'final_amount': 0,
                'delivery_receiver': 'string',
                'delivery_phone': 'string',
                'delivery_address': 'string',
                'delivery_latitude': 0,
                'delivery_longitude': 0,
                'customer_id': 0,
                'order_details': process_order_details_data(order_details_obj),
                'order_image_urls': [
                    {
                        'image_url': 'string'
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
                print('Save order to database successfully!')
    else:
        print('Cannot detect order details from image')


def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def process_img(bytes_str):
    delay = 2
    time.sleep(delay)

    try:
        # Get image from its bytes string
        img = cv2.imdecode(np.fromstring(
            bytes_str, np.uint8), cv2.IMREAD_COLOR)

        order_details_obj = process(img)

        print('Completed to analyze image!')

        job = q.enqueue(
            save_orders, order_details_obj, retry=Retry(max=5))  # Retry max to 5 times before pop action from queue

    except Exception as error:
        raise RuntimeError(error)


def download_and_process_img(record_name, record_path):
    storage.child(
        f'images/{record_name}').download(record_path)

    with open(record_path, 'rb') as record:
        process_img(record.read())
