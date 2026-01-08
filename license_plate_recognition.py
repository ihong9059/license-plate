#!/usr/bin/env python3
"""
삼성폰 IP Webcam을 이용한 자동차 번호판 인식 시스템

사용법:
    1. 삼성폰에서 IP Webcam 앱 실행 후 "Start server" 탭
    2. 아래 PHONE_IP를 삼성폰 IP로 변경
    3. python license_plate_recognition.py 실행
"""

import cv2
import numpy as np
import urllib.request
import re
from datetime import datetime
import time
import sys

# ============ 설정 ============
PHONE_IP = "192.168.0.100"  # 삼성폰 IP 주소 (변경 필요!)
SNAPSHOT_URL = f"http://{PHONE_IP}:8080/shot.jpg"

# 한국 번호판 패턴
PLATE_PATTERNS = [
    r'\d{2,3}[가-힣]\d{4}',           # 12가3456, 123가4567
    r'[가-힣]{2}\d{2}[가-힣]\d{4}',   # 서울12가3456
]

# EasyOCR 리더 (전역 변수)
reader = None


def init_ocr():
    """EasyOCR 초기화"""
    global reader
    print("EasyOCR 초기화 중... (첫 실행 시 모델 다운로드)")
    import easyocr
    reader = easyocr.Reader(['ko', 'en'], gpu=False)
    print("EasyOCR 준비 완료!")
    return reader


def get_snapshot(url=SNAPSHOT_URL):
    """IP Webcam에서 스냅샷 가져오기"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
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

    # 대비 향상 (CLAHE)
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


def recognize_plate(img):
    """번호판 문자 인식"""
    global reader

    if reader is None:
        init_ocr()

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
                    'raw_text': text
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
        # 영역 추출 (약간 여유 있게)
        margin = 5
        y1 = max(0, y - margin)
        y2 = min(img.shape[0], y + h + margin)
        x1 = max(0, x - margin)
        x2 = min(img.shape[1], x + w + margin)

        roi = img[y1:y2, x1:x2]

        # 번호판 인식
        plates = recognize_plate(roi)

        if plates:
            for plate_info in plates:
                all_plates.append(plate_info)

                # 인식된 영역 표시
                cv2.rectangle(display_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_img, plate_info['plate'],
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.9, (0, 255, 0), 2)

    # 후보 영역에서 못 찾았으면 전체 이미지에서 시도
    if not all_plates:
        plates = recognize_plate(img)
        all_plates.extend(plates)

    return display_img, all_plates


def test_connection():
    """IP Webcam 연결 테스트"""
    print(f"\n연결 테스트: {SNAPSHOT_URL}")
    img = get_snapshot()

    if img is None:
        print("연결 실패!")
        print("\n확인 사항:")
        print("1. 삼성폰에서 IP Webcam 앱 실행 후 'Start server' 탭")
        print(f"2. PHONE_IP를 올바른 IP로 변경 (현재: {PHONE_IP})")
        print("3. 폰과 라즈베리파이가 같은 네트워크에 있는지 확인")
        return False

    print(f"연결 성공! 이미지 크기: {img.shape}")
    return True


def main():
    """메인 함수 - 실시간 번호판 인식"""
    print("=" * 50)
    print("자동차 번호판 인식 시스템")
    print(f"IP Webcam 주소: {SNAPSHOT_URL}")
    print("=" * 50)

    # 연결 테스트
    if not test_connection():
        sys.exit(1)

    # OCR 초기화
    init_ocr()

    print("\n번호판 인식을 시작합니다...")
    print("'q' 키를 누르면 종료합니다.\n")

    detected_plates = set()  # 중복 방지

    while True:
        # 스냅샷 가져오기
        img = get_snapshot()

        if img is None:
            print("이미지를 가져올 수 없습니다. 재시도 중...")
            time.sleep(1)
            continue

        # 번호판 인식
        display_img, plates = process_frame(img)

        # 인식 결과 출력
        if plates:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for plate_info in plates:
                plate = plate_info['plate']
                if plate not in detected_plates:
                    detected_plates.add(plate)
                    print(f"[{timestamp}] 새 번호판 인식: {plate} "
                          f"(신뢰도: {plate_info['confidence']:.2f})")

        # 이미지 표시 (GUI가 있는 경우)
        try:
            cv2.imshow("License Plate Recognition", display_img)
            key = cv2.waitKey(500) & 0xFF  # 0.5초 대기
            if key == ord('q'):
                break
        except Exception:
            # GUI가 없는 경우
            time.sleep(0.5)

    cv2.destroyAllWindows()
    print("\n인식된 번호판 목록:")
    for plate in detected_plates:
        print(f"  - {plate}")
    print("\n프로그램 종료")


if __name__ == "__main__":
    main()
