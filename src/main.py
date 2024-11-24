from pipeline import VideoPipeline  # Import from pipeline.py within the same src package
from camera import Camera
from viewer import VideoViewer
import cv2

def main():
    # Create pipeline with effects
    pipeline = VideoPipeline()
    
    # Initialize camera and viewer
    camera = Camera()
    viewer = VideoViewer()
    
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
            
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # Cleanup
        camera.release()
        viewer.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()