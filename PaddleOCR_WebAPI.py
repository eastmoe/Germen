#基于百度飞浆的OCR程序
#https://www.paddlepaddle.org.cn/hubdetail?name=chinese_ocr_db_crnn_server&en_category=TextRecognition
import requests
import json
import cv2
import base64
import datetime

print(datetime.datetime.now())

def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data. tobytes()).decode('utf8')

# 发送HTTP请求
data = {'images':[cv2_to_base64(cv2.imread("./NovelPictures/sample.png"))]}
headers = {"Content-type": "application/json"}
#url = "http://127.0.0.1:8866/predict/chinese_ocr_db_crnn_server"
url = "http://192.168.31.174:8866/predict/chinese_ocr_db_crnn_server"
r = requests.post(url=url, headers=headers, data=json.dumps(data))

# 打印预测结果
print(r.json()["results"])

print(datetime.datetime.now())