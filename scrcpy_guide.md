# 삼성 스마트폰 카메라를 라즈베리 파이에서 보기 (scrcpy)

## 개요

이 가이드는 삼성 안드로이드 스마트폰의 화면(카메라 포함)을 USB 케이블을 통해 라즈베리 파이에 미러링하고, VNC로 원격에서 확인하는 방법을 설명합니다.

```
[삼성 스마트폰] --USB케이블--> [라즈베리 파이] --VNC--> [원격 PC/노트북]
```

## 준비물

- 삼성 안드로이드 스마트폰
- USB 케이블 (데이터 전송 가능한 케이블)
- 라즈베리 파이 (Raspberry Pi OS 설치됨)
- VNC 접속 환경

---

# 1단계: 삼성 스마트폰 설정

## 1.1 개발자 옵션 활성화

삼성폰에서 개발자 옵션을 먼저 활성화해야 합니다.

1. **설정** 앱을 엽니다
2. **휴대전화 정보**를 탭합니다
3. **소프트웨어 정보**를 탭합니다
4. **빌드번호**를 **7번 연속** 탭합니다
5. "개발자 모드가 활성화되었습니다" 메시지가 나타납니다

```
설정 → 휴대전화 정보 → 소프트웨어 정보 → 빌드번호 (7번 탭)
```

## 1.2 USB 디버깅 활성화

1. **설정** 앱을 엽니다
2. **개발자 옵션**을 탭합니다 (맨 아래쪽에 새로 생김)
3. **USB 디버깅**을 찾아서 **켜기**로 설정합니다
4. 경고 메시지가 나오면 **확인**을 탭합니다

```
설정 → 개발자 옵션 → USB 디버깅 → 켜기
```

## 1.3 USB 설정 확인

USB 케이블로 연결했을 때 "파일 전송" 또는 "MTP" 모드로 설정되어야 합니다.

1. USB 케이블을 연결합니다
2. 화면 상단을 아래로 스와이프합니다
3. **USB 연결 알림**을 탭합니다
4. **파일 전송/Android Auto**를 선택합니다

---

# 2단계: 라즈베리 파이 설정

## 2.1 시스템 업데이트

터미널을 열고 다음 명령어를 실행합니다:

```bash
sudo apt update
sudo apt upgrade -y
```

## 2.2 scrcpy 설치

```bash
sudo apt install scrcpy adb -y
```

설치 확인:
```bash
scrcpy --version
adb --version
```

## 2.3 ADB 서버 시작

```bash
adb start-server
```

---

# 3단계: USB 연결 및 권한 허용

## 3.1 USB 케이블 연결

1. USB 케이블로 삼성폰과 라즈베리 파이를 연결합니다
2. 삼성폰 화면에 **"USB 디버깅을 허용하시겠습니까?"** 팝업이 나타납니다
3. **"이 컴퓨터에서 항상 허용"**에 체크합니다
4. **허용**을 탭합니다

> **중요**: 이 팝업이 나타나지 않으면 USB 케이블이 데이터 전송을 지원하지 않는 충전 전용 케이블일 수 있습니다.

## 3.2 연결 확인

터미널에서 다음 명령어로 연결을 확인합니다:

```bash
adb devices
```

정상 연결 시 출력 예시:
```
List of devices attached
XXXXXXXXXXXXXXX    device
```

"unauthorized"로 표시되면 스마트폰에서 USB 디버깅 허용 팝업을 확인하세요.

---

# 4단계: scrcpy 실행

## 4.1 기본 실행 (VNC용)

VNC에서 보려면 DISPLAY 환경변수를 설정해야 합니다:

```bash
DISPLAY=:0 scrcpy
```

## 4.2 실행 옵션

### 창 크기 조절
```bash
DISPLAY=:0 scrcpy --window-width 800 --window-height 600
```

### 전체 화면
```bash
DISPLAY=:0 scrcpy --fullscreen
```

### 해상도 제한 (성능 향상)
```bash
DISPLAY=:0 scrcpy --max-size 1024
```

### 비트레이트 조절 (화질/성능 균형)
```bash
DISPLAY=:0 scrcpy --video-bit-rate 4M
```

### 회전 고정
```bash
# 가로 모드 고정
DISPLAY=:0 scrcpy --rotation 1

# 세로 모드 고정
DISPLAY=:0 scrcpy --rotation 0
```

### 읽기 전용 (터치 비활성화)
```bash
DISPLAY=:0 scrcpy --no-control
```

## 4.3 권장 설정 (카메라용)

카메라 영상을 원활하게 보려면:

```bash
DISPLAY=:0 scrcpy --max-size 1280 --video-bit-rate 8M --rotation 1
```

---

# 5단계: 카메라 영상 보기

## 5.1 카메라 앱 실행

1. scrcpy 창이 열리면 스마트폰 화면이 보입니다
2. scrcpy 창에서 마우스로 **카메라 앱**을 터치/클릭합니다
3. 또는 스마트폰에서 직접 카메라 앱을 실행합니다
4. 카메라 영상이 scrcpy 창에 실시간으로 표시됩니다

## 5.2 카메라 앱 바로 실행 (명령어)

scrcpy 실행과 동시에 카메라 앱을 열 수 있습니다:

```bash
adb shell am start -a android.media.action.VIDEO_CAPTURE
DISPLAY=:0 scrcpy --max-size 1280
```

---

# 6단계: 유용한 단축키

scrcpy 창에서 사용할 수 있는 키보드 단축키:

| 단축키 | 기능 |
|--------|------|
| `Ctrl + F` | 전체 화면 전환 |
| `Ctrl + G` | 창 크기를 1:1로 조절 |
| `Ctrl + X` | 창 크기를 화면에 맞춤 |
| `Ctrl + R` | 화면 회전 |
| `Ctrl + H` | 홈 버튼 |
| `Ctrl + B` | 뒤로 가기 |
| `Ctrl + S` | 앱 전환 버튼 |
| `Ctrl + O` | 화면 끄기 |
| `Ctrl + Shift + O` | 화면 켜기 |
| `Ctrl + N` | 알림창 열기 |
| `마우스 우클릭` | 뒤로 가기 |
| `마우스 가운데 클릭` | 홈 버튼 |

---

# 7단계: 자동 실행 스크립트

## 7.1 스크립트 생성

편리하게 사용할 수 있는 스크립트를 만듭니다:

```bash
nano ~/phone_camera.sh
```

다음 내용을 입력합니다:

```bash
#!/bin/bash
echo "삼성폰 카메라 미러링을 시작합니다..."
echo "USB 케이블이 연결되어 있는지 확인하세요."
echo ""

# ADB 서버 시작
adb start-server

# 장치 연결 확인
DEVICE=$(adb devices | grep -w "device" | head -1)

if [ -z "$DEVICE" ]; then
    echo "오류: 연결된 장치가 없습니다."
    echo "1. USB 케이블 연결을 확인하세요"
    echo "2. 스마트폰에서 USB 디버깅을 허용했는지 확인하세요"
    exit 1
fi

echo "장치가 연결되었습니다!"
echo "scrcpy를 시작합니다..."
echo ""

# scrcpy 실행 (카메라용 최적화 설정)
DISPLAY=:0 scrcpy --max-size 1280 --video-bit-rate 8M --window-title "Phone Camera"
```

## 7.2 실행 권한 부여

```bash
chmod +x ~/phone_camera.sh
```

## 7.3 스크립트 실행

```bash
~/phone_camera.sh
```

---

# 8단계: 문제 해결

## 문제 1: "adb devices"에서 장치가 안 보임

**원인**: USB 디버깅이 허용되지 않았거나, USB 모드가 잘못됨

**해결**:
1. 스마트폰에서 USB 디버깅 허용 팝업을 확인
2. USB 연결 모드를 "파일 전송"으로 변경
3. USB 케이블을 데이터 전송용으로 교체
4. ADB 서버 재시작:
   ```bash
   adb kill-server
   adb start-server
   ```

## 문제 2: "unauthorized" 표시됨

**원인**: 스마트폰에서 디버깅을 허용하지 않음

**해결**:
1. USB 케이블을 분리했다가 다시 연결
2. 스마트폰 화면의 팝업에서 "허용" 선택
3. 그래도 안 되면:
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```

## 문제 3: scrcpy 창이 검은색

**원인**: 디스플레이 설정 문제

**해결**:
```bash
DISPLAY=:0 scrcpy --render-driver=software
```

## 문제 4: 화면이 끊김/지연됨

**원인**: 비트레이트가 너무 높음

**해결**:
```bash
DISPLAY=:0 scrcpy --max-size 800 --video-bit-rate 2M
```

## 문제 5: "ERROR: Could not find any ADB device" 오류

**해결**:
```bash
sudo apt install android-tools-adb -y
adb kill-server
sudo adb start-server
adb devices
```

## 문제 6: VNC에서 scrcpy 창이 안 보임

**원인**: DISPLAY 환경변수 미설정

**해결**:
```bash
export DISPLAY=:0
scrcpy
```

---

# 9단계: 성능 최적화 팁

## 라즈베리 파이 성능 향상

1. **GPU 메모리 늘리기**:
   ```bash
   sudo raspi-config
   ```
   → Performance Options → GPU Memory → 256 설정

2. **불필요한 프로그램 종료**:
   ```bash
   # 현재 실행 중인 프로세스 확인
   htop
   ```

3. **저해상도 사용**:
   ```bash
   DISPLAY=:0 scrcpy --max-size 720 --video-bit-rate 4M
   ```

## 네트워크 지연 최소화 (VNC)

VNC 클라이언트 설정에서:
- 화질을 "Medium" 또는 "Low"로 설정
- 압축률을 높임

---

# 명령어 요약

| 용도 | 명령어 |
|------|--------|
| 설치 | `sudo apt install scrcpy adb -y` |
| 장치 확인 | `adb devices` |
| 기본 실행 | `DISPLAY=:0 scrcpy` |
| 카메라 최적화 | `DISPLAY=:0 scrcpy --max-size 1280 --video-bit-rate 8M` |
| 전체 화면 | `DISPLAY=:0 scrcpy --fullscreen` |
| ADB 서버 재시작 | `adb kill-server && adb start-server` |

---

# 참고 자료

- scrcpy GitHub: https://github.com/Genymobile/scrcpy
- 라즈베리 파이 IP: 192.168.0.26
- VNC 접속 주소: 192.168.0.26:5900
