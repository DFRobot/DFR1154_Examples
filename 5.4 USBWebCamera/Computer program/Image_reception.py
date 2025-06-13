import cv2

def capture_video(device_id: int = 0) -> None:
    """
    Capture video from a camera device and display it in a window.
    
    Args:
        device_id: Camera device ID (default is 0 for the primary camera).
    """
    # Initialize the video capture object
    cap = cv2.VideoCapture(device_id)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        raise IOError(f"Error: Cannot open camera with ID {device_id}")
    
    try:
        window_name = "Camera Feed"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            
            if not ret:
                raise IOError("Error: Cannot receive frame (stream end?). Exiting...")
            
            # Display the resulting frame
            cv2.imshow(window_name, frame)
            
            # Press 'q' on the keyboard to exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
                
            # Optional: Resize window with mouse drag
            cv2.setWindowProperty(window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    
    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
        print("Camera resources released and windows closed.")

if __name__ == "__main__":
    try:
        capture_video()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
