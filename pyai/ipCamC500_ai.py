# 1단계 : 선행 준비 : ip카메라를 준비한다.
# ip카메라의 제조 회사 홈페이지에서 관련 네트워크를 설정하여 마무리한다.
# 제조 회사의 VMS 프로그램 설치하여 ip, 암호, RTSP 프로토콜 활성화 한다.

# 2단계 : 파이썬과 프론트를 연동하는 mqtt api를 활용한다.
# mqtt : 실시간 출력 프로토콜
# https://underflow101.tistory.com/22   -> MQTT 프로토콜 이란?
# mqtt 브로커용 프로그램 모스키토 api를 활용한다.
# https://mosquitto.org/download/ -> 모스키토 다운로드 사이트 : 꼭 버전 맞춰야하므로 2.0.18 사용한다.(수업자료 cctv_py_boot)
# 모스키토 환경설정 변경 :    C:\Program Files\mosquitto\mosquitto.conf
# MQTT 기본 리스너 설정
# listener 1883
# protocol mqtt
#
# # WebSocket 리스너 설정
# listener 9001
# protocol websockets
#
# # 익명의 접속 허용
# allow_anonymous true

# 방화벽 설정 추가 -> 실행 -> wf.msc 1883, 9001 Open
# 터미널에서 환경설정 적용 실행
# mosquitto -c mosquitto.conf -v
# 이래도 안되면 services.msc에 가서 mosquitto.broker 재실행
# 3개의 서버가 동시에 실행이 되어야 한다.

import base64
import io
from PIL import Image
import numpy as np
import json
from ultralytics import YOLO
import paho.mqtt.client as mqtt     # 브로커 추가 -> cmd 에서 mosquitto 실행중 이여야 함.
import cv2
import time

model = YOLO('yolov8n.pt')
client = mqtt.Client()      # mosquitto -c mosquitto.conf
topic = '/camera/objects'   # 경로
client.connect('localhost', 1883, 60)

# 연결용 함수
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

# 객체 감지용 사각박스 함수
def get_colors(num_colors):
    np.random.seed(0)
    colors = [tuple(np.random.randint(0, 255, 3).tolist()) for _ in range(num_colors)]
    return colors

class_names = model.names   # 모델에서 받은 클래스 이름
num_classes = len(class_names)  # 클래스 번호
colors = get_colors(num_classes)    # 사각박스 컬러 색

client.on_connect = on_connect  # 클라이언트 연결 정보
cap = cv2.VideoCapture('rtsp://admin:mbc312AI!!@192.168.0.8:554/taem1')   # rtsp 정보(VMS 참고)

# https://deep-learning-study.tistory.com/107 -> VideoCapture 설명

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# bRec = False
# prevTime = 0

# ------------------------------------------------ 전 처리 -----------------------------------
def detect_objects(image: np.array):
    results = model(image, verbose=False)
    class_names = model.names

    for result in results:
        boxes = result.boxes.xyxy
        confidences = result.boxes.conf
        class_ids = result.boxes.cls
        for box, confidences, class_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = map(int, box)
            label = class_names[int(class_id)]
            cv2.rectangle(image, (x1,y1), (x2,y2), colors[int(class_id)], 2)
            cv2.putText(image, f'{label} {confidences:.2f}', (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, colors[int(class_id)], 2)
    return image

# 객체 탐지 반복용 루프
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    result_image = detect_objects(frame)

    _, buffer = cv2.imencode('.jpg', result_image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    payload = json.dumps({'image': jpg_as_text})
    client.publish(topic, payload)
    cv2.imshow('Frame', result_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):   # 영상 출력 중에 q가 입력이 되면 종료
        break
        
cap.release()   # VideoCapture
cv2.destroyAllWindows() # 창 닫기
client.disconnect() # 연결 해제

# 터미널에서 python ipCamC500_ai.py 입력

# cmd 에서 C:\Program Files\mosquitto>mosquitto -c mosquitto.conf -v