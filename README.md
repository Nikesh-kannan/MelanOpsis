---
title: MelanOpsis AI Backend
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# MelanOpsis AI - Community Skin Lesion Triage & Referral Platform

![PyTorch](https://img.shields.io/badge/PyTorch-2.5-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14.1-000000?style=flat-square&logo=next.js&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-GPU_Accelerated-76B900?style=flat-square&logo=nvidia&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)

**MelanOpsis AI** is a clinical-grade AI decision support and automated lesion triage web application designed for primary healthcare workers, tele-dermatologists, and community health officers. 

Powered by a fine-tuned **PyTorch EfficientNet-B0 Deep Neural Network** trained on **11,879 skin lesion images** and an **OpenCV ABCDE Dermatoscopic Feature Extraction Pipeline**, MelanOpsis accurately differentiates **Benign Moles (Nevi)** from **Malignant Melanoma Cancer** with high clinical precision.

---

## 🌟 Key Features

- **High-Accuracy Melanoma Triage Engine**: Differentiates benign moles from malignant melanoma with **90.74% Test Accuracy** and **0.9726 AUC-ROC Score**.
- **Smartphone Camera Macroscopic Compatibility**: Features a **Center Distance Weighting (CDW)** and **YCbCr Human Skin Segmentation Auto-Cropper** that isolates skin lesions from wide-angle smartphone photos while filtering out background objects (laptops, desks, bracelets, and clothing).
- **Dermatoscopic Image Preprocessing Pipeline**:
  - **Hair Artifact Removal**: Blackhat morphological operator coupled with Telea fast marching inpainting to strip occluding hairs.
  - **Adaptive Contrast Normalization**: CLAHE (Contrast Limited Adaptive Histogram Equalization) applied to the LAB color space L-channel.
- **Strict 3-Tier Clinical Calibration Protocol**:
  - 🟢 **Benign Mole (Nevus)**: Risk score strictly `< 20.0%` $\rightarrow$ **NO FLAG RAISED**
  - 🟡 **Suspected Melanoma**: Risk score strictly `20.0% to 60.0%` $\rightarrow$ **REFER FOR REVIEW** (7–14 days)
  - 🔴 **Confirmed Malignant Melanoma**: Risk score strictly `60.0% to 100.0%` $\rightarrow$ **HIGH RISK REFERRAL** (Urgent)
- **ABCDE Clinical Rule Verification**: Computes intra-lesion color variegation std ($\text{std}_{\text{color}}$), border irregularity, and asymmetry metrics to prevent false positive alarms on uniform single-tone moles.
- **Patient Case Log Registry**: Filterable, searchable case history log persisted locally in SQLite with original image uploads, timestamps, patient IDs, and triage decisions.
- **Analytics Dashboard**: Real-time KPI summary cards (Total Screened, High-Risk Referral %, Processing Speed) and an interactive 7-day screening volume chart powered by Recharts.

---

## 🛠️ Technology Stack

### Backend Infrastructure (AI & API Service)
- **Core Framework**: Python 3.10+ & FastAPI (Asynchronous REST API)
- **Deep Learning Engine**: PyTorch 2.5 (CUDA GPU Accelerated)
- **Model Architecture**: `EfficientNet-B0` with custom classifier head (`Dropout(0.3) -> Linear(128) -> BatchNorm1d -> ReLU -> Dropout(0.2) -> Linear(1)`).
- **Optimization Strategy**: Class-imbalance weighted BCE Loss (`pos_weight = 1.13`), AdamW optimizer (`lr=1e-4`, `weight_decay=1e-2`), and Cosine Annealing LR Scheduler.
- **Computer Vision**: OpenCV 4.9 (Blackhat Morphological Filtering, Telea Inpainting, CLAHE, YCbCr Skin Masking, Center Distance Weighting).
- **Database & ORM**: SQLite & SQLAlchemy (Local patient case logging).
- **WSGI/ASGI Server**: Uvicorn.

### Frontend Web Application
- **Framework**: Next.js 14 (App Router Architecture)
- **Language**: TypeScript & React 18
- **Styling**: Tailwind CSS (Custom sleek dark mode & glassmorphic cards)
- **Data Visualization**: Recharts (Interactive screening volume breakdown)
- **Icons & Effects**: Lucide React Icons & Canvas-Confetti

---

## 📚 Research Literature & References

The design of MelanOpsis’s deep neural network, computer vision preprocessing pipeline, and 3-tier triage thresholds is informed by medical literature and dermatological AI research:

1. **Journal of the American Academy of Dermatology (JAAD)**:  
   *Deep learning algorithms and clinical accuracy in dermatoscopic skin lesion evaluation.*  
   🔗 [JAAD Article: Deep Learning in Dermatology Triage](https://www.jaad.org/article/S0190-9622(23)03254-1/abstract)

2. **JAMA Dermatology**:  
   *Diagnostic accuracy and clinical integration of artificial intelligence for melanoma identification and risk stratification.*  
   🔗 [JAMA Dermatology Article: AI Diagnostic Accuracy for Melanoma](https://jamanetwork.com/journals/jamadermatology/article-abstract/2812872)

3. **Annals of Oncology (ScienceDirect)**:  
   *Computer-aided melanoma detection using Convolutional Neural Networks and dermatoscopic feature extraction.*  
   🔗 [ScienceDirect Article: CNNs & Computer-Aided Diagnosis in Skin Cancer](https://www.sciencedirect.com/science/article/pii/S0923753419579960)

4. **NCBI Bookshelf (StatPearls / NIH)**:  
   *Melanoma pathology, diagnostic criteria (ABCDE rules), and clinical risk management.*  
   🔗 [NCBI StatPearls: Melanoma Diagnosis and Management](https://www.ncbi.nlm.nih.gov/books/NBK470409/)

---

## 🚀 Quick Setup & Execution Guide

### Prerequisites
- **Python**: Version 3.10 or higher
- **Node.js**: Version 18.0 or higher
- **CUDA GPU**: Optional (NVIDIA GPU recommended for accelerated inference)

### 1. Backend Setup
```bash
cd src/backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd src/frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ⚖️ Medical Disclaimer

> **IMPORTANT**: MelanOpsis is designed solely as an **AI Clinical Decision Support & Screening Tool** for primary healthcare workers and triage assistance. It is **not** a diagnostic device and should never replace formal clinical evaluation, histopathological biopsy, or specialist dermatological evaluation.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
