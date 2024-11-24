from pipeline import VideoPipeline  # Import from pipeline.py within the same src package
from camera import Camera
from viewer import VideoViewer
from warp import WarpingEffect
import cv2

def main():
    # Initialize camera and viewer
    camera = Camera()
    viewer = VideoViewer()
    
    # Read the first frame to get frame dimensions
    first_frame = camera.read()
    if first_frame is None:
        print("Unable to read from camera.")
        return
    frame_height, frame_width = first_frame.shape[:2]
    
    # Create pipeline with effects
    pipeline = VideoPipeline()
    
    # Add WarpingEffect as the last step
    warp_effect = WarpingEffect(viewer, frame_width, frame_height)
    pipeline.add_effect(warp_effect)
    
    try:
        while True:
            # Read frame from camera
            frame = camera.read()
            if frame is None:
                break
            
            # Process frame through pipeline
            processed_frame = pipeline.process_frame(frame)
            
            # Display processed frame
            viewer.show_frame(processed_frame)
            
            # Check for 'q' key press or window close
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or viewer.is_window_closed():
                print("Exiting application.")
                break
    
    finally:
        # Cleanup
        camera.release()
        viewer.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()