import cv2

class VideoViewer:
    def __init__(self, window_name: str = "Video Feed"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name)
    
    def show_frame(self, frame):
        cv2.imshow(self.window_name, frame)
    
    def close(self):
        cv2.destroyWindow(self.window_name)