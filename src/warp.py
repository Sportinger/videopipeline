import cv2
import numpy as np
from pipeline import VideoEffect
from viewer import VideoViewer

class WarpingEffect(VideoEffect):
    def __init__(self, viewer: VideoViewer, frame_width: int, frame_height: int, mode='warp', show_overlays=True):
        """
        Base class for Warping Effects.
        :param viewer: Associated VideoViewer instance.
        :param frame_width: Width of the video frame.
        :param frame_height: Height of the video frame.
        :param mode: Mode of warping ('warp' or 'input').
        :param show_overlays: Whether to show draggable points and connecting lines.
        """
        self.viewer = viewer
        self.mode = mode  # 'warp' or 'input'
        self.show_overlays = show_overlays

        # Initialize corner points at the frame corners
        self.initialize_points(frame_width, frame_height)

        self.selected_point = None
        self.dragging = False
        self.warp_matrix = None
        self.dst_size = (frame_width, frame_height)  # Desired output size
        self.point_radius = 10

        self.set_mode_colors()
        self.viewer.set_mouse_callback(self.mouse_callback)
        self.compute_warp_matrix()

    def initialize_points(self, frame_width, frame_height):
        """
        Initialize corner points based on the mode.
        """
        if self.mode == 'warp':
            # Points define the output warped area
            self.points = [
                (0, 0),  # Top-left
                (frame_width - 1, 0),  # Top-right
                (frame_width - 1, frame_height - 1),  # Bottom-right
                (0, frame_height - 1)  # Bottom-left
            ]
        elif self.mode == 'input':
            # Points define the input slice area
            self.points = [
                (0, 0),  # Top-left
                (frame_width - 1, 0),  # Top-right
                (frame_width - 1, frame_height - 1),  # Bottom-right
                (0, frame_height - 1)  # Bottom-left
            ]

    def set_mode_colors(self):
        """
        Set colors based on the current mode.
        """
        if self.mode == 'warp':
            self.point_color = (255, 0, 0)  # Blue
            self.point_color_selected = (0, 255, 0)  # Green when selected
            self.line_color = (255, 0, 0)
        elif self.mode == 'input':
            self.point_color = (0, 255, 0)  # Green
            self.point_color_selected = (255, 0, 0)  # Blue when selected
            self.line_color = (0, 255, 0)

    def set_mode(self, mode):
        """
        Switch the mode of the warping effect.
        """
        self.mode = mode
        self.set_mode_colors()
        self.compute_warp_matrix()

    def mouse_callback(self, event, x, y, flags, param):
        """
        Handle mouse events for dragging points.
        """
        if self.show_overlays:
            active_points = self.points

            if event == cv2.EVENT_LBUTTONDOWN:
                # Check if clicking near an existing point for dragging
                for idx, point in enumerate(active_points):
                    if self.is_near(point, (x, y)):
                        self.selected_point = idx
                        self.dragging = True
                        print(f"Selected point {idx + 1} for dragging ({self.mode} mode).")
                        return
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.dragging and self.selected_point is not None:
                    # Clamp point within frame boundaries
                    x_clamped = max(0, min(x, self.dst_size[0] - 1))
                    y_clamped = max(0, min(y, self.dst_size[1] - 1))
                    active_points[self.selected_point] = (x_clamped, y_clamped)
                    self.compute_warp_matrix()
            elif event == cv2.EVENT_LBUTTONUP:
                if self.dragging:
                    print(f"Released point {self.selected_point + 1}.")
                    self.dragging = False
                    self.selected_point = None

    def is_near(self, point, pos, threshold=15):
        """
        Check if a position is near a given point.
        """
        return np.hypot(point[0] - pos[0], point[1] - pos[1]) < threshold

    def compute_warp_matrix(self):
        """
        Compute the perspective warp matrix based on current points.
        """
        try:
            if self.mode == 'warp':
                # Define the source points (corners of the original frame)
                src_pts = np.float32([
                    [0, 0],
                    [self.dst_size[0] - 1, 0],
                    [self.dst_size[0] - 1, self.dst_size[1] - 1],
                    [0, self.dst_size[1] - 1]
                ])
                # Define the destination points (current positions of the draggable points)
                dst_pts = np.float32(self.points)
            elif self.mode == 'input':
                # Define the source points (current positions of the draggable points)
                src_pts = np.float32(self.points)
                # Define the destination points (corners of the original frame)
                dst_pts = np.float32([
                    [0, 0],
                    [self.dst_size[0] - 1, 0],
                    [self.dst_size[0] - 1, self.dst_size[1] - 1],
                    [0, self.dst_size[1] - 1]
                ])
            
            # Compute the perspective transform matrix
            self.warp_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
            print(f"Warp matrix computed for mode: {self.mode}")
        except cv2.error as e:
            print(f"Error computing warp matrix: {e}")
            self.warp_matrix = None

    def process(self, frame):
        """
        Apply the warp to the frame and handle overlays based on the mode.
        """
        if self.warp_matrix is not None:
            if self.mode == 'warp':
                # Apply the warp to the frame
                warped = cv2.warpPerspective(frame, self.warp_matrix, self.dst_size)

                if self.show_overlays:
                    # Draw the output points
                    for idx, point in enumerate(self.points):
                        color = self.point_color_selected if idx == self.selected_point else self.point_color
                        cv2.circle(warped, point, self.point_radius, color, -1)
                        cv2.putText(warped, f'O{idx +1}', (point[0] + 15, point[1] + 15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Draw connecting lines
                    cv2.line(warped, self.points[0], self.points[1], self.line_color, 2)
                    cv2.line(warped, self.points[1], self.points[2], self.line_color, 2)
                    cv2.line(warped, self.points[2], self.points[3], self.line_color, 2)
                    cv2.line(warped, self.points[3], self.points[0], self.line_color, 2)

                return warped

            elif self.mode == 'input':
                # Show unwarped frame with input points
                display_frame = frame.copy()

                if self.show_overlays:
                    # Draw the input points
                    for idx, point in enumerate(self.points):
                        color = self.point_color_selected if idx == self.selected_point else self.point_color
                        cv2.circle(display_frame, point, self.point_radius, color, -1)
                        cv2.putText(display_frame, f'I{idx +1}', (point[0] + 15, point[1] + 15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Draw connecting lines
                    cv2.line(display_frame, self.points[0], self.points[1], self.line_color, 2)
                    cv2.line(display_frame, self.points[1], self.points[2], self.line_color, 2)
                    cv2.line(display_frame, self.points[2], self.points[3], self.line_color, 2)
                    cv2.line(display_frame, self.points[3], self.points[0], self.line_color, 2)

                return display_frame

        return frame