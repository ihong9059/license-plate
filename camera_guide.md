# Raspberry Pi Camera V2 (8MP) 조작 가이드

## 카메라 정보
- 센서: Sony IMX219
- 해상도: 3280x2464 (8MP)
- 연결: CSI 커넥터

## 카메라 확인

```bash
# 카메라 감지 확인
rpicam-hello --list-cameras

# 레거시 방식 확인
vcgencmd get_camera
```

## 사진 촬영

```bash
# 기본 촬영
rpicam-still -o photo.jpg

# 해상도 지정
rpicam-still --width 1920 --height 1080 -o photo.jpg

# 타임아웃 지정 (2초 후 촬영)
rpicam-still -t 2000 -o photo.jpg
```

## 동영상 녹화

```bash
# 10초 녹화
rpicam-vid -t 10000 -o video.h264

# 해상도/프레임레이트 지정
rpicam-vid -t 10000 --width 1280 --height 720 --framerate 30 -o video.h264

# 무제한 녹화 (Ctrl+C로 종료)
rpicam-vid -t 0 -o video.h264
```

## 미리보기

### 모니터 직접 연결 시
```bash
# 5초간 미리보기
rpicam-hello -t 5000

# 계속 미리보기 (Ctrl+C로 종료)
rpicam-hello -t 0
```

### VNC 원격 접속 시
```bash
# Qt 미리보기 사용 (VNC에서 볼 수 있음)
DISPLAY=:0 rpicam-hello --qt-preview -t 0

# 녹화하면서 미리보기
DISPLAY=:0 rpicam-vid --qt-preview -t 10000 -o video.h264
```

## 웹 브라우저 스트리밍

### 스트리밍 서버 스크립트 (camera_stream.py)
```python
#!/usr/bin/env python3
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import io
import socketserver
from http import server
from threading import Condition

PAGE = """\
<!DOCTYPE html>
<html>
<head><title>Camera Stream</title></head>
<body style="margin:0;background:#000;display:flex;justify-content:center;align-items:center;height:100vh;">
<img src="stream.mjpg" style="max-width:100%;max-height:100vh;"/>
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception:
                pass
        else:
            self.send_error(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output))

print("Camera streaming server started!")
print("Open in browser: http://<IP>:8080")

try:
    address = ('', 8080)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
```

### 사용법
```bash
# 스트리밍 시작
python3 camera_stream.py

# 브라우저에서 접속
# http://192.168.0.26:8080

# 스트리밍 중지
pkill -f camera_stream.py
```

## VLC로 TCP 스트리밍

### 서버 시작
```bash
rpicam-vid -t 0 --width 1280 --height 720 --framerate 30 --listen -o tcp://0.0.0.0:8888
```

### VLC에서 접속
```
tcp/h264://192.168.0.26:8888
```

## 지원 해상도 및 프레임레이트

| 해상도 | 프레임레이트 |
|--------|-------------|
| 640x480 | 103 fps |
| 1640x1232 | 42 fps |
| 1920x1080 | 48 fps |
| 3280x2464 | 21 fps |

## 참고
- 스트리밍 스크립트 위치: `/home/uttec/camera_stream.py`
- IP 주소: `192.168.0.26`
