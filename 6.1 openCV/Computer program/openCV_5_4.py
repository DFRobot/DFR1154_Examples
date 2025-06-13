import cv2  
import numpy as np  
import time  


class CameraContourDetector:  
    def __init__(self, camera_index=0):  
        """Initialize the camera and parameters"""  
        self.cap = cv2.VideoCapture(camera_index)  
        if not self.cap.isOpened():  
            raise RuntimeError("Failed to open the camera")  
  
        # Image processing parameters  
        self.blur_kernel = (11, 11)  
        self.canny_threshold1 = 30  
        self.canny_threshold2 = 150  
        self.dilation_kernel = np.ones((3, 3), np.uint8)  # Larger kernel for better effect  
        self.dilation_iterations = 2  
  
        # Create windows  
        cv2.namedWindow("Original Video", cv2.WINDOW_NORMAL)  
        cv2.namedWindow("Canny Edges", cv2.WINDOW_NORMAL)  
        cv2.namedWindow("Contour Detection", cv2.WINDOW_NORMAL)  
  
        # Resize windows for better visibility  
        cv2.resizeWindow("Original Video", 640, 480)  
        cv2.resizeWindow("Canny Edges", 640, 480)  
        cv2.resizeWindow("Contour Detection", 640, 480)  

    def preprocess_frame(self, frame):  
        """Preprocess the image frame"""  
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
        blurred = cv2.GaussianBlur(gray, self.blur_kernel, 0)  
        return blurred  

    def detect_edges(self, preprocessed_frame):  
        """Detect edges in the image"""  
        edges = cv2.Canny(preprocessed_frame, self.canny_threshold1, self.canny_threshold2)  
        dilated = cv2.dilate(edges, self.dilation_kernel, iterations=self.dilation_iterations)  
        return dilated  

    def find_and_draw_contours(self, frame, edges):  
        """Find and draw contours"""  
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
        contour_image = frame.copy()  
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)  
  
        # Calculate and display the number of contours  
        contour_count = len(contours)  
        cv2.putText(contour_image, f"Contour Count: {contour_count}", (10, 30),  
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  
  
        return contour_image, contour_count  

    def run(self):  
        """Run real-time contour detection"""  
        try:  
            while True:  
                ret, frame = self.cap.read()  
                if not ret:  
                    print("Failed to get the image frame")  
                    break  
  
                # Flip the image horizontally for intuitive display  
                frame = cv2.flip(frame, 1)  
  
                # Process the image  
                preprocessed = self.preprocess_frame(frame)  
                edges = self.detect_edges(preprocessed)  
                contour_image, count = self.find_and_draw_contours(frame, edges)  
  
                # Display results  
                cv2.imshow("Original Video", frame)  
                cv2.imshow("Canny Edges", edges)  
                cv2.imshow("Contour Detection", contour_image)  
  
                # Handle key presses  
                key = cv2.waitKey(1) & 0xFF  
                if key == ord('q'):  # Press 'q' to exit  
                    break  
                elif key == ord('s'):  # Press 's' to save the current frame and contours  
                    self.save_frame(frame, edges, contour_image, count)  
        finally:  
            # Release resources  
            self.cleanup()  

    def save_frame(self, frame, edges, contour_image, count):  
        """Save the current frame and processing results"""  
        timestamp = time.strftime("%Y%m%d-%H%M%S")  
        cv2.imwrite(f"frame_{timestamp}.jpg", frame)  
        cv2.imwrite(f"edges_{timestamp}.jpg", edges)  
        cv2.imwrite(f"contours_{timestamp}.jpg", contour_image)  
        print(f"Images saved. Contour count: {count}")  

    def cleanup(self):  
        """Release resources and close windows"""  
        self.cap.release()  
        cv2.destroyAllWindows()  


if __name__ == "__main__":  
    try:  
        detector = CameraContourDetector()  
        detector.run()  
    except Exception as e:  
        print(f"Program error: {e}")
