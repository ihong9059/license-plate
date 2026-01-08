# 삼성폰 IP Webcam을 이용한 번호판 인식 시스템

## 개요

삼성 스마트폰의 카메라를 IP Webcam 앱을 통해 라즈베리 파이로 스트리밍하고, AI로 자동차 번호판을 인식하는 시스템입니다.

```
[삼성폰 카메라] --WiFi/USB테더링--> [라즈베리 파이] --AI처리--> [번호판 인식 결과]
      │                                    │
   IP Webcam 앱                    OpenCV + EasyOCR
```

## 시스템 요구사항

### 삼성폰
- Android 5.0 이상
- IP Webcam 앱 (무료)

### 라즈베리 파이
- Raspberry Pi OS
- Python 3.9+
- 최소 2GB RAM (4GB 권장)

---

# 1단계: 삼성폰에 IP Webcam 앱 설치

## 1.1 앱 설치

1. 삼성폰에서 **Google Play Store** 열기
2. **"IP Webcam"** 검색 (개발자: Pavel Khlebovich)
3. **설치** 버튼 탭

## 1.2 앱 설정

IP Webcam 앱을 실행하고 다음과 같이 설정합니다:

### 비디오 설정
```
Video preferences (비디오 설정)
├── Main camera: Back camera (후면 카메라)
├── Video resolution: 1280x720 (권장) 또는 1920x1080
├── Quality: 80-90%
└── FPS limit: 30
```

### 연결 설정
```
Connection settings (연결 설정)
├── Port: 8080 (기본값)
└── Login/Password: 필요시 설정 (보안)
```

### 전원 설정
```
Power management (전원 관리)
├── Disable notification: 체크
├── Prevent sleep while plugged in: 체크
└── Stream on device boot: 필요시 체크
```

## 1.3 스트리밍 시작

1. 앱 하단으로 스크롤
2. **"Start server"** (서버 시작) 탭
3. 화면에 표시되는 IP 주소 확인 (예: `http://192.168.0.100:8080`)

## 1.4 스트림 URL 형식

IP Webcam은 여러 형식의 스트림을 제공합니다:

| 용도 | URL |
|------|-----|
| 웹 인터페이스 | `http://폰IP:8080/` |
| JPEG 스냅샷 | `http://폰IP:8080/shot.jpg` |
| MJPEG 스트림 | `http://폰IP:8080/video` |
| 고급 설정 | `http://폰IP:8080/settings` |

---

# 2단계: 라즈베리 파이 환경 설정

## 2.1 시스템 업데이트

```bash
sudo apt update
sudo apt upgrade -y
```

## 2.2 Python 가상환경 생성 (권장)

```bash
# 가상환경 생성
python3 -m venv ~/venv_lpr

# 가상환경 활성화
source ~/venv_lpr/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

## 2.3 필수 시스템 패키지 설치

```bash
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libcanberra-gtk3-module \
    libhdf5-dev \
    libhdf5-serial-dev \
    gfortran
```

## 2.4 Python 라이브러리 설치

```bash
# 가상환경 활성화 (아직 안 했다면)
source ~/venv_lpr/bin/activate

# OpenCV 설치
pip install opencv-python-headless

# EasyOCR 설치 (한글 지원)
pip install easyocr

# 추가 라이브러리
pip install numpy pillow requests
```

> **참고**: EasyOCR 첫 실행 시 한글 모델을 자동 다운로드합니다 (약 100MB)

---

# 3단계: 연결 테스트

## 3.1 네트워크 연결 확인

삼성폰과 라즈베리 파이가 같은 네트워크에 있어야 합니다.

### WiFi 연결
- 같은 공유기에 연결

### USB 테더링 (권장 - 더 안정적)
1. 삼성폰: **설정** → **연결** → **모바일 핫스팟 및 테더링**
2. **USB 테더링** 활성화
3. 라즈베리 파이에서 IP 확인:
   ```bash
   ip addr show usb0
   ```

## 3.2 스트림 접속 테스트

```bash
# 스냅샷 테스트
curl -o test.jpg http://폰IP:8080/shot.jpg

# 이미지 확인
ls -la test.jpg
```

## 3.3 Python 연결 테스트

```python
import cv2
import urllib.request
import numpy as np

# 삼성폰 IP 주소로 변경하세요
PHONE_IP = "192.168.0.100"
URL = f"http://{PHONE_IP}:8080/shot.jpg"

# 이미지 가져오기
with urllib.request.urlopen(URL) as response:
    img_array = np.array(bytearray(response.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

print(f"이미지 크기: {img.shape}")
cv2.imwrite("test_capture.jpg", img)
print("test_capture.jpg 저장 완료")
```

---

# 4단계: 번호판 인식 프로그램

## 4.1 기본 번호판 인식 코드

```python
#!/usr/bin/env python3
"""
삼성폰 IP Webcam을 이용한 자동차 번호판 인식 시스템
"""

import cv2
import numpy as np
import urllib.request
import easyocr
import re
from datetime import datetime

# ============ 설정 ============
PHONE_IP = "192.168.0.100"  # 삼성폰 IP 주소
SNAPSHOT_URL = f"http://{PHONE_IP}:8080/shot.jpg"
STREAM_URL = f"http://{PHONE_IP}:8080/video"

# EasyOCR 리더 초기화 (한글 + 영어)
print("EasyOCR 초기화 중... (첫 실행 시 모델 다운로드)")
reader = easyocr.Reader(['ko', 'en'], gpu=False)
print("EasyOCR 준비 완료!")

# 한국 번호판 패턴
# 예: 12가3456, 서울12가3456, 123가4567
PLATE_PATTERNS = [
    r'\d{2,3}[가-힣]\d{4}',      # 12가3456, 123가4567
    r'[가-힣]{2}\d{2}[가-힣]\d{4}',  # 서울12가3456
]


def get_snapshot():
    """IP Webcam에서 스냅샷 가져오기"""
    try:
        with urllib.request.urlopen(SNAPSHOT_URL, timeout=5) as response:
            img_array = np.array(bytearray(response.read()), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
    except Exception as e:
        print(f"스냅샷 가져오기 실패: {e}")
        return None


def preprocess_image(img):
    """번호판 인식을 위한 이미지 전처리"""
    # 그레이스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 노이즈 제거
    denoised = cv2.bilateralFilter(gray, 11, 17, 17)

    # 대비 향상
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    return enhanced


def find_plate_candidates(img):
    """번호판 후보 영역 찾기"""
    # 엣지 검출
    edges = cv2.Canny(img, 30, 200)

    # 컨투어 찾기
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for contour in contours:
        # 컨투어 근사화
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # 4개의 꼭지점을 가진 사각형 찾기
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)

            # 한국 번호판 비율: 약 2:1 ~ 5:1
            if 2.0 <= aspect_ratio <= 5.0 and w > 100:
                candidates.append((x, y, w, h))

    return candidates


def recognize_plate(img, reader):
    """번호판 문자 인식"""
    # EasyOCR로 텍스트 인식
    results = reader.readtext(img)

    recognized_plates = []
    for (bbox, text, confidence) in results:
        # 공백 제거
        text = text.replace(" ", "")

        # 번호판 패턴 매칭
        for pattern in PLATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                plate_number = match.group()
                recognized_plates.append({
                    'plate': plate_number,
                    'confidence': confidence,
                    'bbox': bbox
                })

    return recognized_plates


def process_frame(img):
    """프레임 처리 및 번호판 인식"""
    if img is None:
        return None, []

    # 원본 이미지 복사
    display_img = img.copy()

    # 이미지 전처리
    processed = preprocess_image(img)

    # 번호판 후보 영역 찾기
    candidates = find_plate_candidates(processed)

    all_plates = []

    # 후보 영역에서 번호판 인식
    for (x, y, w, h) in candidates:
        # 영역 추출
        roi = img[y:y+h, x:x+w]

        # 번호판 인식
        plates = recognize_plate(roi, reader)

        if plates:
            for plate_info in plates:
                all_plates.append(plate_info)

                # 인식된 영역 표시
                cv2.rectangle(display_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_img, plate_info['plate'],
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.9, (0, 255, 0), 2)

    # 전체 이미지에서도 인식 시도
    if not all_plates:
        plates = recognize_plate(img, reader)
        all_plates.extend(plates)

    return display_img, all_plates


def main():
    """메인 함수 - 실시간 번호판 인식"""
    print("=" * 50)
    print("자동차 번호판 인식 시스템")
    print(f"IP Webcam 주소: {SNAPSHOT_URL}")
    print("=" * 50)
    print("'q' 키를 누르면 종료합니다.")
    print("")

    while True:
        # 스냅샷 가져오기
        img = get_snapshot()

        if img is None:
            print("이미지를 가져올 수 없습니다. 재시도 중...")
            continue

        # 번호판 인식
        display_img, plates = process_frame(img)

        # 인식 결과 출력
        if plates:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for plate_info in plates:
                print(f"[{timestamp}] 인식된 번호판: {plate_info['plate']} "
                      f"(신뢰도: {plate_info['confidence']:.2f})")

        # 이미지 표시 (GUI가 있는 경우)
        try:
            cv2.imshow("License Plate Recognition", display_img)
            key = cv2.waitKey(500) & 0xFF  # 0.5초 대기
            if key == ord('q'):
                break
        except:
            # GUI가 없는 경우 (SSH 등)
            pass

    cv2.destroyAllWindows()
    print("프로그램 종료")


if __name__ == "__main__":
    main()
```

## 4.2 간단한 테스트 코드

```python
#!/usr/bin/env python3
"""
간단한 번호판 인식 테스트
"""

import cv2
import numpy as np
import urllib.request
import easyocr

# 설정
PHONE_IP = "192.168.0.100"  # 삼성폰 IP로 변경
URL = f"http://{PHONE_IP}:8080/shot.jpg"

# EasyOCR 초기화
print("EasyOCR 초기화 중...")
reader = easyocr.Reader(['ko', 'en'], gpu=False)
print("준비 완료!")

# 이미지 가져오기
print(f"\n{URL} 에서 이미지 가져오는 중...")
with urllib.request.urlopen(URL, timeout=10) as response:
    img_array = np.array(bytearray(response.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

print(f"이미지 크기: {img.shape}")

# OCR 수행
print("\n텍스트 인식 중...")
results = reader.readtext(img)

print("\n===== 인식 결과 =====")
for (bbox, text, confidence) in results:
    print(f"텍스트: {text}, 신뢰도: {confidence:.2f}")

# 결과 이미지 저장
for (bbox, text, confidence) in results:
    pts = np.array(bbox, np.int32)
    cv2.polylines(img, [pts], True, (0, 255, 0), 2)
    cv2.putText(img, text, (int(bbox[0][0]), int(bbox[0][1])-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

cv2.imwrite("result.jpg", img)
print("\nresult.jpg 저장 완료!")
```

---

# 5단계: 실행 방법

## 5.1 IP Webcam 시작 (삼성폰)

1. IP Webcam 앱 실행
2. "Start server" 탭
3. 표시된 IP 주소 확인

## 5.2 번호판 인식 실행 (라즈베리 파이)

```bash
# 가상환경 활성화
source ~/venv_lpr/bin/activate

# 프로젝트 폴더로 이동
cd ~/uttec/번호판

# IP 주소 수정 (코드 내 PHONE_IP 변수)
nano license_plate_recognition.py

# 실행
python license_plate_recognition.py
```

## 5.3 VNC에서 실행 (GUI 표시)

```bash
DISPLAY=:0 python license_plate_recognition.py
```

---

# 6단계: 문제 해결

## 문제 1: 연결 실패

**원인**: 네트워크 연결 문제

**해결**:
```bash
# 폰 IP로 ping 테스트
ping 192.168.0.100

# 포트 확인
curl http://192.168.0.100:8080/
```

## 문제 2: EasyOCR 모델 다운로드 실패

**해결**:
```bash
# 수동 다운로드
pip install --upgrade easyocr
python -c "import easyocr; reader = easyocr.Reader(['ko', 'en'])"
```

## 문제 3: 메모리 부족

**해결**:
```bash
# 스왑 메모리 늘리기
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 문제 4: 인식률이 낮음

**해결**:
- IP Webcam 해상도 높이기 (1080p)
- 조명 개선
- 카메라 각도 조정 (정면에서 촬영)
- 이미지 전처리 강화

---

# 7단계: 성능 최적화

## GPU 가속 (라즈베리 파이 5)

```bash
# CUDA는 지원 안됨, CPU 최적화 사용
pip install opencv-python-headless
```

## 인식 속도 향상

```python
# 이미지 크기 줄이기
img = cv2.resize(img, (640, 480))

# ROI만 처리
# 번호판이 주로 나타나는 영역만 크롭
```

---

# 참고 자료

- IP Webcam: https://play.google.com/store/apps/details?id=com.pas.webcam
- EasyOCR: https://github.com/JaidedAI/EasyOCR
- OpenCV: https://opencv.org/

---

# 파일 구조

```
~/uttec/번호판/
├── camera_guide.md              # 라즈베리파이 카메라 가이드
├── scrcpy_guide.md              # scrcpy 가이드
├── ip_webcam_license_plate_guide.md  # 이 문서
├── license_plate_recognition.py  # 메인 인식 프로그램
└── test_connection.py           # 연결 테스트
```
