from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from ultralytics import YOLO
import cv2
import numpy as np
import time
import base64

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'ojhdsajjasjiavbjjacjnjawuifwuinjsavuuiwusanlnahjbdvihabnwjnfiuwabfiuafiunaf'
socketio = SocketIO(app)
model = YOLO("../models/best.pt")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

global image

@app.route('/')
def index():
    # render image on index.html

    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('image_data')
def handle_image(image_data):
    image_np = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    results = model(image, conf=0.85, verbose=False)
    cv2.imwrite('test.jpg', results[0].plot())  

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
        image =cv2.rectangle(image,(int(fall_box[0].item()),int(fall_box[1].item())),(int(fall_box[2].item()),int(fall_box[3].item())),(0,0,255),2)
    else:
        response = {'fall_detected': False}
    
    response['image'] = base64.b64encode(cv2.imencode('.jpg', image)[1]).decode()
    # print(image_response)
    emit('fall_detection_result', response,broadcast=True)

@socketio.on('test')
def test(data):
    print(data)
    

if __name__ == '__main__':
    socketio.run(app, port=5000, host='0.0.0.0')
