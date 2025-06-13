import cv2
import torch
import time
from yolov5 import YOLOv5
import urllib.request
import numpy as np

url = 'http://192.168.31.115:80/capture'  # ESP32-CAM的IP地址

# Load the YOLOv5 model
model_path = "yolov5s.pt"  # 模型路径
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = YOLOv5(model_path, device=device)

while True:
    img_resp = urllib.request.urlopen(url)  # 从URL获取图像数据
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)  # 将图像数据转换为NumPy数
    frame = cv2.imdecode(imgnp, -1)  # 解码JPEG图像数据

    # 记录处理开始时间
    start_time = time.time()

    # 将帧传递给模型进行预测
    results = model.predict(frame, size=640)  # 调整输入图像大小为640x640

    # 获取预测结果并在图像上绘制
    annotated_frame = results.render()  # YOLOv5库中的render方法

    # 记录处理结束时间
    end_time = time.time()

    # 计算帧率
    processing_time = end_time - start_time
    fps = 1 / processing_time

    # 在图像上绘制帧率
    cv2.putText(annotated_frame[0], f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # 显示带有预测结果的帧
    cv2.imshow("YOLOv5 Detection", annotated_frame[0])

    # 打印详细信息到终端
    print(f"Processed frame in {processing_time:.4f} seconds, FPS: {fps:.2f}")


    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头资源并关闭所有窗口
cap.release()
cv2.destroyAllWindows()
