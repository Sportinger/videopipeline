import cv2
from typing import Callable

class VideoViewer:
    def __init__(self, window_name: str = "Video Feed"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name)
        self.mouse_callback = None
        cv2.setMouseCallback(self.window_name, self.default_mouse_callback)
        self.frame_width = None
        self.frame_height = None
    
    def set_mouse_callback(self, callback: Callable):
        self.mouse_callback = callback
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
    
    def default_mouse_callback(self, event, x, y, flags, param):
        pass
    
    def show_frame(self, frame):
        if self.frame_width is None or self.frame_height is None:
            self.frame_height, self.frame_width = frame.shape[:2]
        cv2.imshow(self.window_name, frame)
    
    def is_window_closed(self):
        # Check if the window has been closed
        # OpenCV does not provide a direct method, but getWindowProperty can be used
        return cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1
    
    def close(self):
        cv2.destroyWindow(self.window_name)