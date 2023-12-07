from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from ultralytics import YOLO
import cv2
import numpy as np
import time

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'ojhdsajjasjiavbjjacjnjawuifwuinjsavuuiwusanlnahjbdvihabnwjnfiuwabfiuafiunaf'
socketio = SocketIO(app)
model = YOLO("../models/best.pt")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('image')
def handle_image(image_data):
    image_np = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    results = model(image, conf=0.85, verbose=False)
    
    fall_box = results[0].boxes.cpu().numpy().xyxy
    print(fall_box.size)
    if fall_box.size > 0:
        fall_box = fall_box[0]
        response = {
            'fall_detected': True,
            'fall_box': {
                'xmin': fall_box[0].item(),
                'ymin': fall_box[1].item(),
                'xmax': fall_box[2].item(),
                'ymax': fall_box[3].item()
            }
        }
    else:
        response = {'fall_detected': False}

    emit('fall_detection_result', response)

if __name__ == '__main__':
    socketio.run(app, port=5000, host='0.0.0.0')
