# OCR 모델 비교 보고서

> 작성일: 2026-01-09
> 목적: 라즈베리파이 기반 번호판/텍스트 인식 시스템에 적합한 OCR 엔진 선택

---

## 1. OCR 엔진 개요

OCR(Optical Character Recognition)은 이미지에서 텍스트를 추출하는 기술입니다. 2025년 기준으로 오픈소스 OCR은 크게 두 가지 접근 방식이 있습니다:

1. **전통적 ML 엔진**: Tesseract, EasyOCR, PaddleOCR
2. **멀티모달 LLM 기반**: TrOCR, GOT-OCR, Qwen-VL

---

## 2. 주요 OCR 엔진 비교

### 2.1 Tesseract OCR

| 항목 | 내용 |
|------|------|
| **개발사** | HP (원개발), Google (2006년~ 유지보수) |
| **기반 기술** | LSTM 기반 (v4.0+) |
| **지원 언어** | 116개 언어 |
| **하드웨어** | CPU 기반 (GPU 지원 제한적) |
| **라이선스** | Apache 2.0 |

**장점:**
- 가볍고 빠름 (CPU만으로 동작)
- 오랜 역사와 안정성
- 라즈베리파이 등 저사양 기기에서 실행 가능
- 풍부한 언어 지원

**단점:**
- 복잡한 레이아웃에서 정확도 낮음
- 기울어진 텍스트 인식 어려움
- 딥러닝 기반 모델 대비 정확도 낮음

**적합한 용도:**
- 저사양 하드웨어
- 간단한 문서 OCR
- 빠른 처리가 필요한 경우

---

### 2.2 EasyOCR

| 항목 | 내용 |
|------|------|
| **개발사** | JaidedAI |
| **기반 기술** | PyTorch 기반 딥러닝 |
| **지원 언어** | 80개+ 언어 |
| **하드웨어** | GPU 권장 (CUDA) |
| **라이선스** | Apache 2.0 |

**장점:**
- 사용하기 쉬운 Python API
- 딥러닝 기반 높은 정확도
- 다양한 스크립트/언어 지원
- 복잡한 이미지에서도 좋은 성능

**단점:**
- GPU 없이는 매우 느림
- 메모리 사용량 높음 (2GB+)
- 라즈베리파이에서 실행 어려움 (OOM)

**적합한 용도:**
- GPU가 있는 서버/PC
- 고정확도가 필요한 경우
- 복잡한 레이아웃 문서

---

### 2.3 PaddleOCR

| 항목 | 내용 |
|------|------|
| **개발사** | Baidu (PaddlePaddle) |
| **기반 기술** | PaddlePaddle 프레임워크 |
| **지원 언어** | 80개+ 언어 |
| **하드웨어** | GPU 권장 |
| **라이선스** | Apache 2.0 |

**장점:**
- 높은 정확도 (특히 중국어/아시아 언어)
- 빠른 처리 속도
- 기울어진 텍스트 인식 가능 (회전 bounding box)
- PP-Structure로 테이블 인식 지원
- 경량 모델 제공 (모바일용)

**단점:**
- 설정/튜닝이 복잡함
- PaddlePaddle 프레임워크 의존성
- 문서가 주로 중국어

**적합한 용도:**
- 아시아 언어 OCR
- 테이블/문서 구조 분석
- 모바일/엣지 디바이스 (경량 모델)

---

### 2.4 TrOCR (Microsoft)

| 항목 | 내용 |
|------|------|
| **개발사** | Microsoft |
| **기반 기술** | Vision Transformer (ViT) + BERT/RoBERTa |
| **지원 언어** | 영어 중심 (다국어 모델 별도) |
| **하드웨어** | GPU 필수 |
| **라이선스** | MIT |

**장점:**
- Transformer 기반 최신 아키텍처
- 손글씨 인식에 뛰어남
- End-to-end 학습 가능

**단점:**
- GPU 필수
- 추론 속도 느림
- 다국어 지원 제한적

**적합한 용도:**
- 연구/실험 목적
- 손글씨 인식
- 커스텀 학습이 필요한 경우

---

### 2.5 MMOCR

| 항목 | 내용 |
|------|------|
| **개발사** | OpenMMLab |
| **기반 기술** | PyTorch (MMDetection 기반) |
| **지원 언어** | 다국어 |
| **하드웨어** | GPU 권장 |
| **라이선스** | Apache 2.0 |

**장점:**
- 모듈화된 설계
- 다양한 OCR 모델 통합
- 커스텀 학습 용이
- 문서 분석 기능

**단점:**
- 복잡한 설정
- GPU 필요

**적합한 용도:**
- OCR 연구
- 커스텀 모델 개발

---

## 3. 성능 비교표

| 엔진 | 정확도 | 속도 | 메모리 | 한글 지원 | 라즈베리파이 |
|------|--------|------|--------|-----------|--------------|
| **Tesseract** | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | ✅ 가능 |
| **EasyOCR** | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ | ❌ 불가 (OOM) |
| **PaddleOCR** | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★★ | ⚠️ 경량모델만 |
| **TrOCR** | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ | ❌ 불가 |
| **MMOCR** | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ❌ 불가 |

---

## 4. 한글 인식 성능 비교

한글 OCR 성능은 학습 데이터와 모델에 따라 크게 달라집니다.

| 엔진 | 한글 정확도 | 특이사항 |
|------|-------------|----------|
| **Tesseract** | 중간 | 기본 kor 데이터 인식률 낮음, 추가 학습 필요 |
| **EasyOCR** | 높음 | 한글 전용 모델 포함, 정확도 우수 |
| **PaddleOCR** | 매우 높음 | 아시아 언어에 특화, 한글 인식 우수 |
| **Pororo** | 높음 | 네이버 개발, 한국어 특화 NLP/OCR |

---

## 5. 라즈베리파이 적합성 분석

### 하드웨어 제약
- **RAM**: 1GB ~ 8GB
- **GPU**: 없음 (CPU만 사용)
- **저장공간**: SD 카드 기반

### 권장 엔진

| 순위 | 엔진 | 이유 |
|------|------|------|
| 1위 | **Tesseract** | CPU만으로 동작, 메모리 효율적 |
| 2위 | **PaddleOCR Lite** | 경량 모델 제공, 모바일/엣지 최적화 |
| 3위 | **Kraken** | 가벼운 대안, 다국어 지원 |

---

## 6. 프로젝트 적용 결론

### 현재 선택: Tesseract OCR

**선택 이유:**
1. 라즈베리파이 1GB RAM에서 유일하게 안정적 실행
2. 한글 언어팩 기본 제공
3. 설치 및 설정 간단
4. Apache 2.0 라이선스

**한계:**
1. 한글 인식률이 딥러닝 모델 대비 낮음
2. 기울어진 텍스트 인식 어려움
3. 복잡한 배경에서 성능 저하

### 향후 개선 방안

1. **Tesseract 한글 학습 데이터 개선**
   - tessdata_best 사용 (더 정확한 모델)
   - 커스텀 학습 데이터 생성

2. **PaddleOCR Lite 테스트**
   - 라즈베리파이 4 (4GB+)에서 테스트
   - 경량 모델로 한글 인식

3. **클라우드 OCR API 활용**
   - Google Cloud Vision API
   - Naver Clova OCR
   - 정확도 높지만 비용 발생

---

## 7. 참고 자료

- [OCR 프레임워크 비교 (Medium)](https://adityamangal98.medium.com/a-researchers-deep-dive-comparing-top-ocr-frameworks-ca6327b3cc86)
- [Tesseract vs EasyOCR vs PaddleOCR 비교](https://toon-beerten.medium.com/ocr-comparison-tesseract-versus-easyocr-vs-paddleocr-vs-mmocr-a362d9c79e66)
- [2025년 최고의 오픈소스 OCR 도구](https://unstract.com/blog/best-opensource-ocr-tools-in-2025/)
- [8가지 오픈소스 OCR 모델 비교](https://modal.com/blog/8-top-open-source-ocr-models-compared)
- [PaddleOCR vs Tesseract 분석](https://www.koncile.ai/en/ressources/paddleocr-analyse-avantages-alternatives-open-source)
- [2025년 OCR 트렌드와 멀티모달 LLM](https://photes.io/blog/posts/ocr-research-trend)

---

## 8. 부록: 설치 명령어

### Tesseract (라즈베리파이)
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-kor
pip install pytesseract
```

### EasyOCR (GPU 서버)
```bash
pip install easyocr
```

### PaddleOCR
```bash
pip install paddlepaddle paddleocr
```

### TrOCR
```bash
pip install transformers
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel
```
