import cv2
from typing import Callable

class VideoViewer:
    def __init__(self, window_name: str = "Video Feed"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name)
        self.mouse_callback = None
        self.option_callback = None
        cv2.setMouseCallback(self.window_name, self.mouse_callback_handler)
        self.frame_width = None
        self.frame_height = None
        # Menu state
        self.show_menu = False
        self.menu_options = ["Switch to Input View", "Switch to Warp View"]
        self.menu_position = (100, 100)  # Default menu position
        self.menu_size = (200, 50)  # Width, Height per option
        self.menu_clicked_option = None

    def set_mouse_callback(self, callback: Callable):
        """
        Set the mouse callback function for the viewer.
        """
        self.mouse_callback = callback

    def set_option_callback(self, callback: Callable):
        """
        Set the option callback function for the context menu.
        """
        self.option_callback = callback

    def mouse_callback_handler(self, event, x, y, flags, param):
        """
        Handle mouse events for context menu and delegate to the assigned callback.
        """
        if self.show_menu:
            if event == cv2.EVENT_LBUTTONDOWN:
                for idx, option in enumerate(self.menu_options):
                    x1 = self.menu_position[0]
                    y1 = self.menu_position[1] + idx * self.menu_size[1]
                    x2 = x1 + self.menu_size[0]
                    y2 = y1 + self.menu_size[1]
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        if self.option_callback:
                            self.option_callback(option)
                        self.show_menu = False
                        print(f"Menu option selected: {option}")
                        return
                # Click outside menu closes it
                self.show_menu = False
                print("Clicked outside menu. Closing menu.")
        else:
            if event == cv2.EVENT_RBUTTONDOWN:
                self.show_menu = True
                self.menu_position = (x, y)
                print(f"Right-click detected at ({x}, {y}). Showing context menu.")
            elif self.mouse_callback:
                # Delegate other mouse events to the assigned callback
                self.mouse_callback(event, x, y, flags, param)

    def show_frame(self, frame):
        """
        Display the frame in the viewer window, including the context menu if active.
        """
        # Draw context menu if needed
        if self.show_menu:
            for idx, option in enumerate(self.menu_options):
                top_left = (self.menu_position[0], self.menu_position[1] + idx * self.menu_size[1])
                bottom_right = (top_left[0] + self.menu_size[0], top_left[1] + self.menu_size[1] - 5)
                cv2.rectangle(frame, top_left, bottom_right, (200, 200, 200), -1)  # Grey background
                cv2.rectangle(frame, top_left, bottom_right, (0, 0, 0), 1)  # Black border
                cv2.putText(frame, option, (top_left[0] + 10, top_left[1] + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.imshow(self.window_name, frame)

    def is_window_closed(self):
        """
        Check if the viewer window has been closed.
        """
        return cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1

    def close(self):
        """
        Close the viewer window.
        """
        cv2.destroyWindow(self.window_name)