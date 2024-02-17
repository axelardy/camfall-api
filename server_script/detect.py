
import time
import threading
from server_script.send_notification import send_notification

class FallDetector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.fall_start_time = None
        self.fall_detected_continuously = False
        self.fall = False  
        self.running = True
        
    def run(self):
        while self.running:
            self.check_fall()
            time.sleep(0.1)  
            
    def update_fall_state(self, fall):

        self.fall = fall
    
    def check_fall(self):

        if self.fall:
            if self.fall_start_time is None:
                self.fall_start_time = time.time()
            elif time.time() - self.fall_start_time >= 5 and not self.fall_detected_continuously:
                print("Fall has been detected continuously for at least 5 seconds.")
                send_notification('CAMERA 1')
                self.fall_detected_continuously = True
        else:
            if self.fall_detected_continuously:
                # Reset the detector when fall ends
                self.reset_detector()
    
    def reset_detector(self):

        self.fall_start_time = None
        self.fall_detected_continuously = False
    
    def stop(self):

        self.running = False
