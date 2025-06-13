import cv2
import urllib.request
import numpy as np
from urllib.error import URLError, HTTPError

def main():
    # IP address of ESP32-CAM
    url = 'http://192.168.31.115:80/capture'
    
    # Create windows
    cv2.namedWindow("Live Transmission", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Edge Detection", cv2.WINDOW_NORMAL)
    
    # Resize windows
    cv2.resizeWindow("Live Transmission", 800, 600)
    cv2.resizeWindow("Edge Detection", 800, 600)
    
    # Initialize timing variables
    frame_count = 0
    start_time = cv2.getTickCount()
    
    print("Press 'q' to exit the program")
    
    while True:
        try:
            # Fetch image
            img_resp = urllib.request.urlopen(url)
            img_data = img_resp.read()
            
        except HTTPError as e:
            print(f"HTTP Error: {e.code}")
            break
        except URLError as e:
            print(f"URL Error: {e.reason}")
            break
        except Exception as e:
            print(f"Unknown error fetching image: {e}")
            break
            
        # Process image
        try:
            img_np = np.frombuffer(img_data, dtype=np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            if img is None:
                print("Failed to decode image")
                continue
                
        except Exception as e:
            print(f"Image processing error: {e}")
            continue
            
        # Image processing
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Gaussian blur and Canny edge detection
            blurred = cv2.GaussianBlur(gray, (11, 11), 0)
            canny = cv2.Canny(blurred, 30, 150, apertureSize=3)
            
            # Dilation
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(canny, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Draw contours
            img_contours = img.copy()
            cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 2)
            
            # Calculate FPS
            frame_count += 1
            if frame_count >= 30:
                end_time = cv2.getTickCount()
                fps = frame_count / ((end_time - start_time) / cv2.getTickFrequency())
                frame_count = 0
                start_time = cv2.getTickCount()
                cv2.putText(img_contours, f"FPS: {fps:.2f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Display images
            cv2.imshow("Live Transmission", img_contours)
            cv2.imshow("Edge Detection", canny)
            
        except Exception as e:
            print(f"Image processing error: {e}")
            continue
            
        # Exit condition
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cv2.destroyAllWindows()
    print("Program exited")

if __name__ == "__main__":
    main()    