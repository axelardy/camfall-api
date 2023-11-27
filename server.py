from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import time


app = Flask(__name__)
model = YOLO("../models/best.pt")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route("/predict", methods=["POST"])
def detect_fall():
    image = request.files["image"]
    image_np = np.fromfile(image, np.uint8)

    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    results = model(image, conf=0.75, verbose=False)

    fall_box = results[0].boxes.cpu().numpy().xyxy

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
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=5000,host='0.0.0.0')