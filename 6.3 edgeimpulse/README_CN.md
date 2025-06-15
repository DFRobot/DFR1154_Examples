- [English Version](https://github.com/DFRobot/DFR1154_Examples/blob/master/6.3%20edgeimpulse/README.md)

该示例代码使用了在edgeimpulse训练的Person_Detection_inferencing模型进行人形识别，通过串口可查看识别结果，通过网页视频流可查看摄像头画面。


**步骤**

1. 将Person_Detection_inferencing文件夹放入Arduino IDE安装目录的libraries中

2. 启动Arduino IDE，在示例代码中选择Person_Detection_inferencing -> edge_camera，烧录代码

3. 打开串口监视器（波特率115200），根据提示输入WiFi SSID和Password，即可连接WiFi。

4. 连接成功后通过浏览器访问串口监视器打印的IP地址即可监控后台，通过“Start Stream”按钮即可获取图像流。
