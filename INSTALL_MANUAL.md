# 라즈베리 파이 자동차 번호판 인식 시스템 - 상세 설치 매뉴얼

> **최종 업데이트**: 2026-01-08
> **대상**: Raspberry Pi OS (64-bit)
> **목적**: 삼성 스마트폰 IP Webcam을 이용한 한글 자동차 번호판 인식

---

## 목차

1. [시스템 요구사항](#1-시스템-요구사항)
2. [1단계: 스마트폰 IP Webcam 설정](#2-1단계-스마트폰-ip-webcam-설정)
3. [2단계: 라즈베리 파이 기본 설정](#3-2단계-라즈베리-파이-기본-설정)
4. [3단계: Python 가상환경 설정](#4-3단계-python-가상환경-설정)
5. [4단계: 시스템 의존성 패키지 설치](#5-4단계-시스템-의존성-패키지-설치)
6. [5단계: Python 라이브러리 설치](#6-5단계-python-라이브러리-설치)
7. [6단계: EasyOCR 한글 모델 설치](#7-6단계-easyocr-한글-모델-설치)
8. [7단계: 연결 테스트](#8-7단계-연결-테스트)
9. [8단계: 번호판 인식 실행](#9-8단계-번호판-인식-실행)
10. [문제 해결 가이드](#10-문제-해결-가이드)
11. [성능 최적화](#11-성능-최적화)

---

## 1. 시스템 요구사항

### 라즈베리 파이
| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| 모델 | Raspberry Pi 3B+ | Raspberry Pi 4/5 |
| RAM | 2GB | 4GB 이상 |
| 저장공간 | 16GB SD카드 | 32GB 이상 |
| OS | Raspberry Pi OS (64-bit) | 최신 버전 |

### 스마트폰
- Android 5.0 이상
- IP Webcam 앱 설치 가능
- WiFi 또는 USB 테더링 가능

### 네트워크
- 스마트폰과 라즈베리 파이가 같은 네트워크에 연결
- 또는 USB 테더링 사용 (더 안정적)

---

## 2. 1단계: 스마트폰 IP Webcam 설정

### 2.1 앱 설치

1. Google Play Store 열기
2. **"IP Webcam"** 검색 (개발자: Pavel Khlebovich)
3. **설치** 클릭

### 2.2 앱 설정

IP Webcam 앱을 실행하고 아래 설정을 적용합니다:

#### 비디오 설정 (Video preferences)
```
Main camera        : Back camera (후면 카메라)
Video resolution   : 1280x720 (권장) 또는 1920x1080
Quality            : 80-90%
FPS limit          : 30
```

#### 연결 설정 (Connection settings)
```
Port               : 8080 (기본값)
Login              : (비워두기 또는 설정)
Password           : (비워두기 또는 설정)
```

#### 전원 설정 (Power management)
```
Disable notification          : 체크
Prevent sleep while plugged in: 체크
Stream on device boot         : 필요시 체크
```

### 2.3 서버 시작

1. 앱 하단으로 스크롤
2. **"Start server"** 탭
3. 화면에 표시되는 IP 주소 기록
   - 예: `http://192.168.0.33:8080`

### 2.4 사용 가능한 URL 형식

| 용도 | URL |
|------|-----|
| 웹 인터페이스 | `http://폰IP:8080/` |
| JPEG 스냅샷 | `http://폰IP:8080/shot.jpg` |
| MJPEG 스트림 | `http://폰IP:8080/video` |
| 설정 페이지 | `http://폰IP:8080/settings` |

---

## 3. 2단계: 라즈베리 파이 기본 설정

### 3.1 시스템 업데이트

```bash
sudo apt update
sudo apt upgrade -y
```

**예상 소요 시간**: 5-15분

### 3.2 스왑 메모리 설정 (중요!)

EasyOCR은 메모리를 많이 사용하므로 스왑을 늘립니다:

```bash
# 현재 스왑 확인
free -h

# 스왑 비활성화
sudo dphys-swapfile swapoff

# 스왑 크기 설정 (2GB)
sudo nano /etc/dphys-swapfile
```

`/etc/dphys-swapfile` 파일에서:
```
CONF_SWAPSIZE=2048
```

저장 후 (Ctrl+O, Enter, Ctrl+X):
```bash
# 스왑 재설정 및 활성화
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 확인
free -h
```

**예상 소요 시간**: 2-3분

---

## 4. 3단계: Python 가상환경 설정

### 4.1 가상환경 생성

```bash
# 가상환경 생성
python3 -m venv ~/venv_lpr

# 가상환경 활성화
source ~/venv_lpr/bin/activate
```

활성화되면 프롬프트가 `(venv_lpr)` 로 시작합니다.

### 4.2 pip 업그레이드

```bash
pip install --upgrade pip
```

### 4.3 가상환경 자동 활성화 (선택사항)

매번 활성화하기 번거로우면 `.bashrc`에 추가:

```bash
echo "source ~/venv_lpr/bin/activate" >> ~/.bashrc
```

---

## 5. 4단계: 시스템 의존성 패키지 설치

### 5.1 필수 패키지 설치

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
    gfortran \
    libopenblas-dev \
    cmake \
    build-essential
```

**예상 소요 시간**: 5-10분

### 5.2 설치 확인

```bash
dpkg -l | grep -E "libatlas|libjpeg|libhdf5"
```

---

## 6. 5단계: Python 라이브러리 설치

### 6.1 가상환경 활성화 확인

```bash
source ~/venv_lpr/bin/activate
which python  # /home/uttec/venv_lpr/bin/python 출력되어야 함
```

### 6.2 NumPy 설치 (먼저)

```bash
pip install numpy
```

**예상 소요 시간**: 2-3분

### 6.3 OpenCV 설치

```bash
pip install opencv-python-headless
```

**예상 소요 시간**: 3-5분

### 6.4 PyTorch 설치 (EasyOCR 의존성)

라즈베리 파이에서는 CPU 버전만 사용 가능합니다:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**예상 소요 시간**: 10-20분 (인터넷 속도에 따라)

> **중요**: 이 단계에서 메모리 부족으로 실패할 수 있습니다. 스왑이 2GB 이상인지 확인하세요.

### 6.5 EasyOCR 설치

```bash
pip install easyocr
```

**예상 소요 시간**: 3-5분

### 6.6 추가 라이브러리 설치

```bash
pip install pillow requests
```

### 6.7 설치 확인

```bash
pip list | grep -E "easyocr|opencv|torch|numpy"
```

예상 출력:
```
easyocr                1.7.x
numpy                  2.x.x
opencv-python-headless 4.x.x
torch                  2.x.x
torchvision            0.x.x
```

---

## 7. 6단계: EasyOCR 한글 모델 설치

### 7.1 모델 자동 다운로드

EasyOCR은 첫 실행 시 모델을 자동 다운로드합니다. 하지만 안정성을 위해 미리 다운로드하는 것을 권장합니다.

```bash
source ~/venv_lpr/bin/activate

python3 << 'EOF'
import easyocr
print("EasyOCR 한글 모델 다운로드 시작...")
print("(약 100MB, 인터넷 속도에 따라 2-5분 소요)")
reader = easyocr.Reader(['ko', 'en'], gpu=False)
print("다운로드 완료!")
print("모델 준비 완료!")
EOF
```

**예상 소요 시간**: 2-5분

### 7.2 모델 다운로드 확인

```bash
ls -la ~/.EasyOCR/model/
```

예상 출력:
```
-rw-rw-r-- 1 uttec uttec 83152330 craft_mlt_25k.pth
-rw-rw-r-- 1 uttec uttec 16081533 korean_g2.pth
```

두 파일이 있어야 합니다:
- `craft_mlt_25k.pth` - 텍스트 검출 모델 (~80MB)
- `korean_g2.pth` - 한글 인식 모델 (~16MB)

### 7.3 수동 다운로드 (자동 다운로드 실패 시)

자동 다운로드가 실패하면 수동으로 다운로드합니다:

```bash
mkdir -p ~/.EasyOCR/model

# 텍스트 검출 모델
wget -O ~/.EasyOCR/model/craft_mlt_25k.pth \
    https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/craft_mlt_25k.pth

# 한글 인식 모델
wget -O ~/.EasyOCR/model/korean_g2.pth \
    https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/korean_g2.pth
```

---

## 8. 7단계: 연결 테스트

### 8.1 네트워크 연결 방법

#### 방법 1: WiFi (같은 공유기 연결)
1. 스마트폰과 라즈베리 파이를 같은 WiFi에 연결
2. IP Webcam 앱에서 표시된 IP 사용

#### 방법 2: USB 테더링 (권장 - 더 안정적)
1. 스마트폰을 USB로 라즈베리 파이에 연결
2. 스마트폰: **설정** → **연결** → **모바일 핫스팟 및 테더링** → **USB 테더링** 활성화
3. 라즈베리 파이에서 IP 확인:
   ```bash
   ip addr show usb0
   ```

### 8.2 ping 테스트

```bash
ping -c 3 192.168.0.33  # 스마트폰 IP로 변경
```

성공 시:
```
3 packets transmitted, 3 received, 0% packet loss
```

### 8.3 스냅샷 테스트

```bash
curl -o test.jpg http://192.168.0.33:8080/shot.jpg
ls -la test.jpg
```

파일 크기가 0보다 크면 성공입니다.

### 8.4 Python 연결 테스트

```bash
source ~/venv_lpr/bin/activate
cd ~/uttec/lisencePlate

python3 test_connection.py
```

또는 직접 실행:

```bash
python3 << 'EOF'
import cv2
import urllib.request
import numpy as np

PHONE_IP = "192.168.0.33"  # 스마트폰 IP로 변경
URL = f"http://{PHONE_IP}:8080/shot.jpg"

print(f"연결 테스트: {URL}")
try:
    with urllib.request.urlopen(URL, timeout=10) as response:
        img_array = np.array(bytearray(response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    print(f"성공! 이미지 크기: {img.shape}")
    cv2.imwrite("test_capture.jpg", img)
    print("test_capture.jpg 저장 완료")
except Exception as e:
    print(f"실패: {e}")
EOF
```

---

## 9. 8단계: 번호판 인식 실행

### 9.1 IP 주소 설정

`license_plate_recognition.py` 파일의 `PHONE_IP` 변수를 스마트폰 IP로 변경:

```bash
nano ~/uttec/lisencePlate/license_plate_recognition.py
```

19번째 줄:
```python
PHONE_IP = "192.168.0.33"  # 여기를 스마트폰 IP로 변경
```

### 9.2 실행

```bash
source ~/venv_lpr/bin/activate
cd ~/uttec/lisencePlate
python3 license_plate_recognition.py
```

### 9.3 VNC에서 GUI와 함께 실행

VNC로 접속한 경우:
```bash
DISPLAY=:0 python3 license_plate_recognition.py
```

### 9.4 예상 출력

```
==================================================
자동차 번호판 인식 시스템
IP Webcam 주소: http://192.168.0.33:8080/shot.jpg
==================================================

연결 테스트: http://192.168.0.33:8080/shot.jpg
연결 성공! 이미지 크기: (720, 1280, 3)
EasyOCR 초기화 중... (첫 실행 시 모델 다운로드)
EasyOCR 준비 완료!

번호판 인식을 시작합니다...
'q' 키를 누르면 종료합니다.

[2026-01-08 22:30:15] 새 번호판 인식: 12가3456 (신뢰도: 0.95)
```

---

## 10. 문제 해결 가이드

### 문제 1: 연결 실패 - "Connection refused"

**원인**: IP Webcam 서버가 시작되지 않음

**해결**:
1. 스마트폰에서 IP Webcam 앱 확인
2. "Start server" 버튼이 눌러졌는지 확인
3. 방화벽이 8080 포트를 차단하는지 확인

### 문제 2: 연결 실패 - "Network is unreachable"

**원인**: 네트워크 연결 문제

**해결**:
```bash
# 라즈베리 파이 네트워크 확인
ip addr show
ping -c 3 192.168.0.1  # 공유기 ping

# 스마트폰 IP 다시 확인
# IP Webcam 앱에서 표시되는 IP 확인
```

### 문제 3: EasyOCR 모델 다운로드 실패

**원인**: 인터넷 연결 불안정 또는 메모리 부족

**해결**:
```bash
# 메모리 확인
free -h

# 스왑 확인 (2GB 이상 권장)
cat /etc/dphys-swapfile | grep CONF_SWAPSIZE

# 수동 다운로드 (위 7.3절 참조)
```

### 문제 4: 메모리 부족 - "Killed" 또는 "MemoryError"

**원인**: RAM + 스왑 부족

**해결**:
```bash
# 스왑 늘리기
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=4096 로 변경
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 불필요한 프로세스 종료
sudo systemctl stop bluetooth
sudo systemctl stop avahi-daemon
```

### 문제 5: 인식률이 낮음

**원인**: 이미지 품질, 조명, 각도

**해결**:
1. IP Webcam 해상도 높이기 (1920x1080)
2. 조명 개선 (번호판에 직접 조명)
3. 카메라 각도 조정 (정면에서 촬영)
4. 카메라 흔들림 방지 (삼각대 사용)

### 문제 6: "cv2.error: OpenCV..."

**원인**: OpenCV 버전 또는 의존성 문제

**해결**:
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless
```

---

## 11. 성능 최적화

### 11.1 이미지 크기 조정

번호판 인식에는 고해상도가 필수는 아닙니다:

```python
# license_plate_recognition.py 수정
img = cv2.resize(img, (640, 480))  # 속도 향상
```

### 11.2 ROI (관심 영역) 설정

번호판이 주로 나타나는 영역만 처리:

```python
# 이미지 하단 절반만 처리
height = img.shape[0]
roi = img[height//2:, :]
```

### 11.3 프레임 스킵

모든 프레임을 처리하지 않고 일정 간격으로:

```python
frame_count = 0
while True:
    frame_count += 1
    if frame_count % 3 != 0:  # 3프레임마다 1번 처리
        continue
    # 처리 코드
```

### 11.4 GPU 가속 (Raspberry Pi 5 해당 없음)

라즈베리 파이에서는 GPU 가속이 지원되지 않습니다. CPU 최적화만 사용합니다.

---

## 빠른 참조 - 명령어 모음

```bash
# 가상환경 활성화
source ~/venv_lpr/bin/activate

# 프로젝트 폴더로 이동
cd ~/uttec/lisencePlate

# 번호판 인식 실행
python3 license_plate_recognition.py

# 연결 테스트
python3 test_connection.py

# 패키지 확인
pip list | grep -E "easyocr|opencv|torch"

# EasyOCR 모델 확인
ls -la ~/.EasyOCR/model/

# 메모리 확인
free -h

# 스왑 확인
cat /etc/dphys-swapfile | grep CONF_SWAPSIZE
```

---

## 파일 구조

```
~/uttec/lisencePlate/
├── INSTALL_MANUAL.md                  # 이 문서 (상세 설치 매뉴얼)
├── ip_webcam_license_plate_guide.md   # IP Webcam 가이드
├── license_plate_recognition.py       # 메인 번호판 인식 프로그램
├── test_connection.py                 # 연결 테스트 스크립트
├── camera_guide.md                    # 라즈베리파이 카메라 가이드
├── scrcpy_guide.md                    # scrcpy 가이드
└── 작업보고서/
    └── 2026-01-08_작업보고서.md        # 작업 기록
```

---

## 문의 및 참고 자료

- **IP Webcam 앱**: https://play.google.com/store/apps/details?id=com.pas.webcam
- **EasyOCR GitHub**: https://github.com/JaidedAI/EasyOCR
- **OpenCV 문서**: https://docs.opencv.org/
