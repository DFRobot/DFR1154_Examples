- [English Version](https://github.com/DFRobot/DFR1154_Examples/blob/master/6.2%20yolo/README.md)

该示例主要演示了电脑端使用yoloV5实现物体分类。

**步骤**

- 给模块烧录代码（使用5.3或5.4章节的代码）
- 安装python环境（https://www.python.org/），如果安装过，请跳过。
- 安装opencv-python库
  - 按下Win+R，输入cmd进入命令窗口
  - 输入“pip install opencv-python” 安装opencv-python库
  - 输入“pip install yolov5” 安装yolov5库
- 打开python的IDLE，File->Open...，选择py文件（如果使用5.3章节示例，请使用yolo_5_3.py；如果使用5.4章节示例请使用yolo_5_4.py），在弹出的新窗口中按下F5，即可看到画面。

注意

- 使用openCV_5_3.py时，请注意修改IP地址参数

- 使用openCV_5_4.py时，请注意修改cap = cv2.VideoCapture(0)参数
