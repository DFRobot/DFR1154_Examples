The sample code uses the Person_Detection_inferencing model trained on Edge Impulse for human form recognition. The recognition results can be viewed through the serial port, and the camera feed can be viewed via the web video stream. 



### Steps

1. Place the *Person_Detection_inferencing* folder into the `libraries` directory of the Arduino IDE installation path. 
2. Launch Arduino IDE, select *Person_Detection_inferencing > edge_camera* from the example codes, and burn the code. 
3. Open the serial monitor (baud rate 115200), enter the WiFi SSID and password as prompted, and connect to WiFi. 
4. After a successful connection, access the IP address printed by the serial monitor via a browser to monitor the background. Click the **Start Stream** button to obtain the image stream.