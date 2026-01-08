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
import pytesseract
from PIL import Image

# ============ 설정 ============
PHONE_IP = "192.168.0.33"  # 삼성폰 IP 주소
SNAPSHOT_URL = f"http://{PHONE_IP}:8080/shot.jpg"

# 한국 번호판 패턴
PLATE_PATTERNS = [
    r'\d{2,3}[가-힣]\d{4}',           # 12가3456, 123가4567
    r'[가-힣]{2}\d{2}[가-힣]\d{4}',   # 서울12가3456
]

# Tesseract config - Korean + English
TESSERACT_CONFIG = '--oem 3 --psm 4 -l kor'  # PSM 4: single column, variable sizes


def init_ocr():
    """Tesseract OCR init"""
    print("Checking Tesseract OCR...")
    try:
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
        print("Tesseract OCR ready!")
        return True
    except Exception as e:
        print(f"Tesseract init failed: {e}")
        return False


def get_snapshot(url=SNAPSHOT_URL):
    """Get snapshot from IP Webcam"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            img_array = np.array(bytearray(response.read()), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
    except Exception as e:
        print(f"Snapshot failed: {e}")
        return None


def preprocess_for_ocr(img):
    """Preprocess image for OCR"""
    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Simple grayscale works best for clear text
    return gray


def read_text_from_image(img):
    """Read Korean/English/numbers from image"""
    results = []

    try:
        # Preprocess image
        processed = preprocess_for_ocr(img)

        # Convert to PIL image
        pil_img = Image.fromarray(processed)

        # OCR with Tesseract
        text = pytesseract.image_to_string(pil_img, config=TESSERACT_CONFIG)

        # Clean text (keep spaces between words)
        text_cleaned = text.strip()

        if text_cleaned:
            # First, check for license plate pattern
            text_no_space = text_cleaned.replace(" ", "").replace("\n", "")
            plate_found = False

            for pattern in PLATE_PATTERNS:
                match = re.search(pattern, text_no_space)
                if match:
                    results.append({
                        'plate': match.group(),
                        'confidence': 0.9,
                        'raw_text': text_cleaned,
                        'type': 'plate'
                    })
                    plate_found = True

            # If no plate pattern, return all recognized text
            if not plate_found and len(text_no_space) > 0:
                results.append({
                    'plate': text_cleaned.replace("\n", " "),
                    'confidence': 0.7,
                    'raw_text': text_cleaned,
                    'type': 'text'
                })

    except Exception as e:
        print(f"OCR Error: {e}")

    return results


def process_frame(img):
    """Process frame and recognize text (optimized for Pi)"""
    if img is None:
        return None, []

    display_img = img.copy()
    h, w = img.shape[:2]

    # Extract center region (30-60% height, 30-70% width)
    y1, y2 = int(h * 0.30), int(h * 0.60)
    x1, x2 = int(w * 0.30), int(w * 0.70)
    center_roi = img[y1:y2, x1:x2]

    # Recognize text
    plates = read_text_from_image(center_roi)

    return display_img, plates


def test_connection():
    """Test IP Webcam connection"""
    print(f"\nConnection test: {SNAPSHOT_URL}")
    img = get_snapshot()

    if img is None:
        print("Connection failed!")
        print("\nCheck:")
        print("1. IP Webcam app running on phone with 'Start server'")
        print(f"2. PHONE_IP is correct (current: {PHONE_IP})")
        print("3. Phone and Pi on same network")
        return False

    print(f"Connected! Image size: {img.shape}")
    return True


def main():
    """Main function - capture on Enter key"""
    print("=" * 50)
    print("License Plate Recognition System")
    print(f"IP Webcam: {SNAPSHOT_URL}")
    print("=" * 50)

    # Connection test
    if not test_connection():
        sys.exit(1)

    # OCR init
    init_ocr()

    print("\n" + "=" * 50)
    print("Usage:")
    print("  - Enter: Capture and recognize")
    print("  - q + Enter: Quit")
    print("=" * 50 + "\n")

    detected_plates = []

    while True:
        try:
            user_input = input(">> Press Enter to capture (q: quit): ").strip().lower()

            if user_input == 'q':
                break

            print("Capturing...")

            # Get snapshot
            img = get_snapshot()

            if img is None:
                print("Cannot get image. Check IP Webcam connection.")
                continue

            # Recognize plate
            display_img, plates = process_frame(img)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Print result
            if plates:
                for plate_info in plates:
                    text = plate_info['plate']
                    text_type = plate_info.get('type', 'text')
                    # Handle encoding for terminal output
                    try:
                        if text_type == 'plate':
                            print(f"\n[{timestamp}] LICENSE PLATE: {text}")
                        else:
                            print(f"\n[{timestamp}] TEXT: {text}")
                    except UnicodeEncodeError:
                        # Fallback: print with unicode escape
                        safe_text = text.encode('unicode_escape').decode('ascii')
                        if text_type == 'plate':
                            print(f"\n[{timestamp}] LICENSE PLATE: {safe_text}")
                        else:
                            print(f"\n[{timestamp}] TEXT: {safe_text}")
                    detected_plates.append({
                        'time': timestamp,
                        'plate': text,
                        'type': text_type
                    })
                    # Save to file (UTF-8)
                    with open('results.txt', 'a', encoding='utf-8') as f:
                        f.write(f"[{timestamp}] {text_type.upper()}: {text}\n")
            else:
                print(f"\n[{timestamp}] No text found.")

            print()

        except KeyboardInterrupt:
            print("\n\nInterrupted")
            break
        except EOFError:
            break

    # Print results
    print("\n" + "=" * 50)
    print("Detected plates:")
    if detected_plates:
        for item in detected_plates:
            print(f"  [{item['time']}] {item['plate']}")
    else:
        print("  (none)")
    print("=" * 50)
    print("Done")


if __name__ == "__main__":
    main()
