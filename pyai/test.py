import requests

url = "http://127.0.0.1:8002/detect"    # 요청 보낼 URL
message = "TEST Message"    # 서버로 전송할 메세지(폼 데이터로 전송)
file_path = "test.JPG"      # 전송할 이미지 파일 경로(py와 같은 경로에 존재해야됨)

with open(file_path, "rb") as file:
    response = requests.post(url, data={"message":message}, files={"file" : file})

print(response.json())