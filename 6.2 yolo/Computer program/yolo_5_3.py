import cv2
import torch
import time
from yolov5 import YOLOv5
import urllib.request
import numpy as np

url = 'http://192.168.0.227:80/capture'  # ESP32-CAM IP address

# Load the YOLOv5 model
model_path = "yolov5s.pt"  # Model path
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = YOLOv5(model_path, device=device)


def decode_frame(img_bytes):
    """Decode image bytes, supporting both JPEG and raw RGB565 input."""
    # Try standard JPEG/PNG decoding first
    frame = cv2.imdecode(np.frombuffer(img_bytes, dtype=np.uint8), -1)
    if frame is not None:
        return frame

    # Fallback: treat as raw RGB565 data (2 bytes per pixel)
    # Infer width from total byte count assuming a 4:3 aspect ratio
    pixel_count = len(img_bytes) // 2
    # Common ESP32-CAM resolutions; pick the closest matching one
    candidates = [(160, 120), (320, 240), (640, 480), (800, 600)]
    width, height = candidates[-1]
    for w, h in candidates:
        if w * h == pixel_count:
            width, height = w, h
            break
    else:
        # Fallback: assume 320x240 if size doesn't match
        width, height = 320, 240

    rgb565 = np.frombuffer(img_bytes, dtype=np.uint16).reshape((height, width))
    # Expand RGB565 (5-6-5) to RGB888
    r = ((rgb565 >> 11) & 0x1F).astype(np.uint8)
    g = ((rgb565 >> 5) & 0x3F).astype(np.uint8)
    b = (rgb565 & 0x1F).astype(np.uint8)
    r = (r * 255 // 31).astype(np.uint8)
    g = (g * 255 // 63).astype(np.uint8)
    b = (b * 255 // 31).astype(np.uint8)
    frame = cv2.merge([b, g, r])  # OpenCV uses BGR order
    return frame


while True:
    img_resp = urllib.request.urlopen(url)  # Fetch image data from URL
    imgnp = img_resp.read()  # Read raw bytes
    frame = decode_frame(imgnp)  # Decode JPEG or RGB565 data

    if frame is None:
        print("Failed to decode frame, skipping...")
        continue

    # Record processing start time
    start_time = time.time()

    # Pass the frame to the model for prediction
    results = model.predict(frame, size=640)  # Resize input to 640x640

    # Get prediction results and draw them on the image
    annotated_frame = results.render()  # render method from the YOLOv5 library

    # Record processing end time
    end_time = time.time()

    # Calculate frame rate
    processing_time = end_time - start_time
    fps = 1 / processing_time

    # Draw FPS on the image
    cv2.putText(annotated_frame[0], f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Display the frame with prediction results
    cv2.imshow("YOLOv5 Detection", annotated_frame[0])

    # Print detailed info to terminal
    print(f"Processed frame in {processing_time:.4f} seconds, FPS: {fps:.2f}")

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close all windows
cv2.destroyAllWindows()
