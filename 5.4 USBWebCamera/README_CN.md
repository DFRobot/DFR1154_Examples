- [English Version](https://github.com/DFRobot/DFR1154_Examples/blob/master/5.4%20USBWebCamera/README.md)

**步骤**

- 给模块烧录bin文件，将模块通过USB连接电脑。
- 安装python环境（https://www.python.org/），如果安装过，请跳过。
- 安装opencv-python库
  - 按下Win+R，输入cmd进入命令窗口
  - 输入“pip install opencv-python” 安装opencv-python库
- 打开python的IDLE，File->Open...，选择Image_reception.py，在弹出的新窗口中按下F5，即可看到画面。

注意：

- 若窗口无画面，可能因为电脑存在多个摄像头，请修改Image_reception.py文件中“device_id”参数再尝试。

bin文件是基于该示例代码编译而出，该示例需在ESP-IDF使用

项目地址：

https://github.com/espressif/esp-iot-solution/tree/master/examples/usb/device/usb_webcam
