import cv2
import numpy as np
from pipeline import VideoEffect
from viewer import VideoViewer

class WarpingEffect(VideoEffect):
    def __init__(self, viewer: VideoViewer, frame_width: int, frame_height: int):
        self.viewer = viewer
        # Initialize corner points at the corners of the frame
        self.points = [
            (0, 0),  # Top-left
            (frame_width - 1, 0),  # Top-right
            (frame_width - 1, frame_height - 1),  # Bottom-right
            (0, frame_height - 1)  # Bottom-left
        ]
        self.selected_point = None
        self.dragging = False
        self.warp_matrix = None
        self.dst_size = (frame_width, frame_height)  # Desired output size
        self.point_radius = 10
        self.point_color = (255, 0, 0)  # Solid blue
        self.point_color_selected = (0, 255, 0)  # Green when selected
        self.viewer.set_mouse_callback(self.mouse_callback)
        self.compute_warp_matrix()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if clicking near an existing point for dragging
            for idx, point in enumerate(self.points):
                if self.is_near(point, (x, y)):
                    self.selected_point = idx
                    self.dragging = True
                    print(f"Selected point {idx + 1} for dragging.")
                    return
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging and self.selected_point is not None:
                self.points[self.selected_point] = (x, y)
                self.compute_warp_matrix()
        elif event == cv2.EVENT_LBUTTONUP:
            if self.dragging:
                print(f"Released point {self.selected_point + 1}.")
                self.dragging = False
                self.selected_point = None

    def is_near(self, point, pos, threshold=15):
        return np.hypot(point[0] - pos[0], point[1] - pos[1]) < threshold

    def compute_warp_matrix(self):
        # Define the source points (corners of the original frame)
        src_pts = np.float32([
            [0, 0],
            [self.dst_size[0] - 1, 0],
            [self.dst_size[0] - 1, self.dst_size[1] - 1],
            [0, self.dst_size[1] - 1]
        ])
        # Define the destination points (current positions of the draggable points)
        dst_pts = np.float32(self.points)
        # Compute the perspective transform matrix
        self.warp_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        print("Warp matrix computed.")

    def process(self, frame):
        if self.warp_matrix is not None:
            # Warp the original frame
            warped = cv2.warpPerspective(frame, self.warp_matrix, self.dst_size)

            # Draw the draggable points on the warped frame
            for idx, point in enumerate(self.points):
                color = self.point_color_selected if idx == self.selected_point else self.point_color
                cv2.circle(warped, point, self.point_radius, color, -1)
                cv2.putText(warped, str(idx + 1), (point[0] + 15, point[1] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Optionally draw lines connecting the points
            cv2.line(warped, self.points[0], self.points[1], (255, 0, 0), 2)
            cv2.line(warped, self.points[1], self.points[2], (255, 0, 0), 2)
            cv2.line(warped, self.points[2], self.points[3], (255, 0, 0), 2)
            cv2.line(warped, self.points[3], self.points[0], (255, 0, 0), 2)

            return warped
        return frame