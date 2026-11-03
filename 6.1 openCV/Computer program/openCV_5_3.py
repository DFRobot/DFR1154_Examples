import cv2
import urllib.request
import numpy as np
from urllib.error import URLError, HTTPError

# ============ Configuration ============
URL = 'http://192.168.31.115:80/capture'

# When the server returns raw RGB565 data, the image dimensions must be provided
# Common ESP32-CAM resolutions: QQVGA 160x120, QVGA 320x240, VGA 640x480
RGB565_WIDTH  = 320
RGB565_HEIGHT = 240

# Input format: 'auto' | 'jpeg' | 'rgb565'
# 'auto' detects the format via the JPEG magic number FFD8
INPUT_FORMAT = 'auto'
# =======================================


def rgb565_to_bgr(buf: bytes, width: int, height: int, little_endian: bool = True) -> np.ndarray:
    """Convert a raw RGB565 byte stream into an OpenCV BGR image."""
    expected = width * height * 2
    if len(buf) < expected:
        raise ValueError(f"Insufficient RGB565 data: expected {expected} bytes, got {len(buf)} bytes")

    # Take only the first `expected` bytes (guard against trailing padding)
    arr = np.frombuffer(buf[:expected], dtype=np.uint8)

    # Assemble 16-bit pixels
    if little_endian:
        # Low byte first
        lo = arr[0::2].astype(np.uint16)
        hi = arr[1::2].astype(np.uint16)
        px = (hi << 8) | lo
    else:
        hi = arr[0::2].astype(np.uint16)
        lo = arr[1::2].astype(np.uint16)
        px = (hi << 8) | lo

    # Extract components and expand to 8 bits
    r5 = (px >> 11) & 0x1F
    g6 = (px >> 5)  & 0x3F
    b5 =  px        & 0x1F

    # Use bit replication to preserve full range (more uniform than simple *255/31)
    r8 = ((r5 << 3) | (r5 >> 2)).astype(np.uint8)
    g8 = ((g6 << 2) | (g6 >> 4)).astype(np.uint8)
    b8 = ((b5 << 3) | (b5 >> 2)).astype(np.uint8)

    # Assemble into a (H, W, 3) BGR image
    bgr = np.dstack((b8.reshape(height, width),
                     g8.reshape(height, width),
                     r8.reshape(height, width)))
    return bgr


def decode_frame(img_data: bytes, fmt: str = 'auto') -> np.ndarray:
    """Decode the byte stream returned by the server into a BGR image according to the format."""
    if fmt == 'auto':
        if len(img_data) >= 2 and img_data[0] == 0xFF and img_data[1] == 0xD8:
            fmt = 'jpeg'
        else:
            fmt = 'rgb565'

    if fmt == 'jpeg':
        img_np = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("JPEG decoding failed")
        return img
    elif fmt == 'rgb565':
        return rgb565_to_bgr(img_data, RGB565_WIDTH, RGB565_HEIGHT, little_endian=True)
    else:
        raise ValueError(f"Unknown format: {fmt}")


def main():
    cv2.namedWindow("Live Transmission", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Edge Detection",    cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Live Transmission", 800, 600)
    cv2.resizeWindow("Edge Detection",    800, 600)

    frame_count = 0
    start_time = cv2.getTickCount()
    detected_fmt = None

    print("Press 'q' to exit the program")

    while True:
        try:
            img_resp = urllib.request.urlopen(URL, timeout=5)
            img_data = img_resp.read()
        except HTTPError as e:
            print(f"HTTP Error: {e.code}"); break
        except URLError as e:
            print(f"URL Error: {e.reason}"); break
        except Exception as e:
            print(f"Unknown error fetching image: {e}"); break

        # ---- Decoding (JPEG / RGB565 compatible) ----
        try:
            img = decode_frame(img_data, INPUT_FORMAT)
            if detected_fmt is None:
                detected_fmt = 'jpeg' if (len(img_data) >= 2 and img_data[:2] == b'\xff\xd8') else 'rgb565'
                print(f"[INFO] Detected input format: {detected_fmt.upper()}  ({len(img_data)} bytes)")
        except Exception as e:
            print(f"Image decoding error: {e}")
            continue

        # ---- Image processing ----
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (11, 11), 0)
            canny = cv2.Canny(blurred, 30, 150, apertureSize=3)

            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(canny, kernel, iterations=1)

            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            img_contours = img.copy()
            cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 2)

            # FPS
            frame_count += 1
            if frame_count >= 30:
                end_time = cv2.getTickCount()
                fps = frame_count / ((end_time - start_time) / cv2.getTickFrequency())
                frame_count = 0
                start_time = cv2.getTickCount()
                cv2.putText(img_contours, f"FPS: {fps:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Live Transmission", img_contours)
            cv2.imshow("Edge Detection", canny)
        except Exception as e:
            print(f"Image processing error: {e}")
            continue

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    print("Program exited")


if __name__ == "__main__":
    main()