#基于百度飞浆的OCR程序使用WebAPI进行OCR(已弃用，因为效率太低且无法使用CPU加速方法或GPU运算。识别一副图需要90s(Ryzen R5 Pro 4650G))
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