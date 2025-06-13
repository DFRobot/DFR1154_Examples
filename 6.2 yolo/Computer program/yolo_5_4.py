import cv2
import torch
import time
from PIL import Image
import torchvision.transforms as transforms

cap = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Failed to open the camera")
    exit()

# Load the YOLOv5 model
model_path = "yolov5s.pt"  # Model path
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load YOLOv5 model using PyTorch Hub
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model = model.to(device)

# Set the model to evaluation mode
model.eval()

# Define preprocessing transformations
transform = transforms.Compose([
    transforms.ToTensor(),
])

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture the frame")
        break
        
    # Record the start time of processing
    start_time = time.time()

    # No need for decoding since 'frame' is already a decoded image
    # Ensure the image format is correct
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Pass the frame to the model for prediction
    results = model(img, size=640)  # Resize the input image to 640x640

    # Get the prediction results and draw them on the image
    annotated_frame = results.render()[0]  # Get the rendered image
    
    # Convert the RGB image back to BGR format (for OpenCV display)
    annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)

    # Record the end time of processing
    end_time = time.time()

    # Calculate the frame rate
    processing_time = end_time - start_time
    fps = 1 / processing_time if processing_time > 0 else 0

    # Draw the FPS on the image
    cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Display the frame with prediction results
    cv2.imshow("YOLOv5 Detection", annotated_frame)

    # Print detailed information to the terminal
    print(f"Processed frame in {processing_time:.4f} seconds, FPS: {fps:.2f}")

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera resource and close all windows
cap.release()
cv2.destroyAllWindows()
