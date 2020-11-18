import os
import requests
import json
import constants
from . import config
from app import app
from flask import request, jsonify
from .routes_executing import process_img, download_and_process_img
from redis import Redis
from rq import Queue, Retry

q = Queue(connection=Redis(host='0.0.0.0', port=6379))


@app.before_first_request
def get_access_token():
    r = requests.post(f'{constants.API_DOMAIN}{constants.AUTHENTICATION_ROUTE}', json={
                      'username': config.username, 'password': config.password})
    access_token = r.json()['access_token']

    with open('access_token.json', 'w') as f:
        json.dump({'access_token': access_token}, f, indent=4)


@app.route('/upload-image', methods=['POST'])
def upload_image():
    q_len = len(q)
    if request.method == 'POST':
        if request.files:
            # Push image's bytes string into queue
            job = q.enqueue(
                process_img, request.files['image'].read(), retry=Retry(max=5))  # Retry 5 times until removed from queue
    return jsonify({'message': 'Image is uploaded successfully!'})


@app.route('/get-image-from-storage', methods=['POST'])
def get_signal():
    if request.method == 'POST':
        try:
            if not os.path.exists('./app/records'):
                os.makedirs('./app/records')
        except OSError:
            print('Error: Creating directory of data')

        response = request.get_json()
        record_name = response['record_name']
        record_path = f'./app/records/{record_name}'

        job = q.enqueue(
            download_and_process_img, record_name, record_path, retry=Retry(max=5))  # Retry 5 times until removed from queue

    return jsonify({'message': 'Image is crawled successfully!'})
