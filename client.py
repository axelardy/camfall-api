import cv2
import requests
import numpy as np

api_url = "http://192.168.31.82:5000/predict"

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    _, img_encoded = cv2.imencode('.jpg', frame)
    files = {'image': ('image.jpg', img_encoded.tobytes(), 'image/jpeg')}

    response = requests.post(api_url, files=files)\
    
    result = response.json()

    if result['fall_detected']:
        fall_location = result['fall_box']
        xmin, ymin, xmax, ymax = int(fall_location['xmin']), int(fall_location['ymin']), int(fall_location['xmax']), int(fall_location['ymax'])

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
    
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()