import cv2
import socketio
import numpy as np

sio = socketio.Client()

api_url = 'http://localhost:5000'

sio.connect(api_url)
cap = cv2.VideoCapture('test.mp4')

new_frame_available = True
result = None

@sio.on('fall_detection_result')
def handle_fall_detection_result(res):
    global result
    result = res

while True:
    ret, frame = cap.read()
    if not ret:
        # Break the loop when the video ends
        break

    _, img_encoded = cv2.imencode('.jpg', frame)
    image_data = img_encoded.tobytes()

    sio.emit('image', image_data)

    # Wait for the result
    while result is None:
        sio.sleep(0)  # Small delay to avoid busy-waiting

    print(result)
    
    if result['fall_detected']:
        fall_location = result['fall_box']
        xmin, ymin, xmax, ymax = (
            int(fall_location['xmin']),
            int(fall_location['ymin']),
            int(fall_location['xmax']),
            int(fall_location['ymax'])
        )

        # Draw a rectangle on the frame
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)

    # Reset the result and flag for the next iteration
    result = None

    # Display the frame with the rectangle
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

sio.disconnect()
cap.release()
cv2.destroyAllWindows()
