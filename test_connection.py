#!/usr/bin/env python3
"""
IP Webcam 연결 테스트 스크립트
"""

import cv2
import numpy as np
import urllib.request
import sys

# 삼성폰 IP 주소 (변경 필요!)
PHONE_IP = "192.168.0.100"
URL = f"http://{PHONE_IP}:8080/shot.jpg"


def test_connection():
    """연결 테스트"""
    print("=" * 50)
    print("IP Webcam 연결 테스트")
    print("=" * 50)
    print(f"\n테스트 URL: {URL}\n")

    try:
        print("연결 시도 중...")
        with urllib.request.urlopen(URL, timeout=10) as response:
            img_array = np.array(bytearray(response.read()), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is not None:
            print(f"연결 성공!")
            print(f"이미지 크기: {img.shape[1]}x{img.shape[0]} (가로x세로)")
            print(f"채널 수: {img.shape[2]}")

            # 테스트 이미지 저장
            cv2.imwrite("test_capture.jpg", img)
            print("\ntest_capture.jpg 저장 완료!")
            return True
        else:
            print("이미지 디코딩 실패")
            return False

    except urllib.error.URLError as e:
        print(f"연결 실패: {e}")
        print("\n확인 사항:")
        print("1. 삼성폰에서 IP Webcam 앱이 실행 중인가요?")
        print("2. 'Start server'를 탭했나요?")
        print(f"3. IP 주소가 맞나요? (현재: {PHONE_IP})")
        print("4. 폰과 라즈베리파이가 같은 네트워크에 있나요?")
        return False

    except Exception as e:
        print(f"오류 발생: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        PHONE_IP = sys.argv[1]
        URL = f"http://{PHONE_IP}:8080/shot.jpg"

    success = test_connection()
    sys.exit(0 if success else 1)
