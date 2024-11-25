from pipeline import VideoPipeline  # Import from pipeline.py within the same src package
from camera import Camera
from viewer import VideoViewer
from warp import WarpingEffect
import cv2

def main():
    # Initialize camera
    camera = Camera()

    # Read the first frame to get frame dimensions
    first_frame = camera.read()
    if first_frame is None:
        print("Unable to read from camera.")
        return
    frame_height, frame_width = first_frame.shape[:2]

    # Initialize view windows
    main_viewer = VideoViewer("Main Viewer")
    input_viewer = VideoViewer("Input Warping Viewer")
    output_viewer = VideoViewer("Output Warping Viewer")

    # Create pipeline
    pipeline = VideoPipeline()

    # Initialize WarpingEffects
    # Input Warping Effect (Mode: 'input', Show Overlays: True)
    input_warp_effect = WarpingEffect(
        viewer=input_viewer,
        frame_width=frame_width,
        frame_height=frame_height,
        mode='input',
        show_overlays=True
    )
    
    # Output Warping Effect (Mode: 'warp', Show Overlays: False)
    output_warp_effect = WarpingEffect(
        viewer=output_viewer,
        frame_width=frame_width,
        frame_height=frame_height,
        mode='warp',
        show_overlays=False
    )

    # Add effects to the pipeline
    # The order of effects is important. Input warp should be applied first.
    pipeline.add_effect(input_warp_effect)
    pipeline.add_effect(output_warp_effect)

    # Define a callback function for menu options (if needed)
    def handle_menu_option(option):
        if option == "Switch to Input View":
            # Toggle to Input View
            input_warp_effect.set_mode('input')
            output_warp_effect.set_mode('warp')
            print("Switched to Input View.")

        elif option == "Switch to Warp View":
            # Toggle to Warp View
            input_warp_effect.set_mode('warp')
            output_warp_effect.set_mode('input')
            print("Switched to Warp View.")

    # Set the option callback for each viewer (if you want separate menus)
    # Here, we set the same callback for simplicity
    main_viewer.set_option_callback(handle_menu_option)
    input_viewer.set_option_callback(handle_menu_option)
    output_viewer.set_option_callback(handle_menu_option)

    try:
        while True:
            # Read frame from camera
            frame = camera.read()
            if frame is None:
                print("No frame captured from camera. Exiting.")
                break

            # Process frame through pipeline
            processed_frame = pipeline.process_frame(frame)

            # Display frames in respective viewers
            main_viewer.show_frame(frame)
            input_viewer.show_frame(input_warp_effect.process(frame))
            output_viewer.show_frame(output_warp_effect.process(processed_frame))

            # Check for 'q' key press or any window close
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or main_viewer.is_window_closed() or input_viewer.is_window_closed() or output_viewer.is_window_closed():
                print("Exiting application.")
                break

    finally:
        # Cleanup
        camera.release()
        main_viewer.close()
        input_viewer.close()
        output_viewer.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()