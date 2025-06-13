**Steps** 

- Flash the BIN file to the module and connect the module to the computer via USB. 
- Install the Python environment (https://www.python.org/). Skip this step if already installed. 
- Install the `opencv-python` library: 
1. Press **Win+R**, type `cmd`, and press Enter to open the command prompt. 
2. Run `pip install opencv-python` to install the library. 
- Open Python IDLE, navigate to **File > Open...**, select the *Image_reception.py* file, and press **F5** in the new window to view the image. 

**Note**:

- If no image appears, the computer may have multiple cameras. Modify the parameter `device_id` in *Image_reception.py* and retry.

The BIN file is compiled based on this example code, which should be used in ESP-IDF. 
**Project URL**: 
https://github.com/espressif/esp-iot-solution/tree/master/examples/usb/device/usb_webcam