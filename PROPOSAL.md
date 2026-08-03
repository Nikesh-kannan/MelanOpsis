# The Pluribus

**Tech for Good 2026** · GDG Coimbatore · Build weekend Aug 8–9, GRD College

**Track:** AI for Good Health & Well-being
**Team code:** TEAM-299

## Problem

Early-stage skin cancer often goes undetected because suspicious skin lesions are mistaken for harmless moles or pimples, and access to dermatologists is limited, especially in rural areas. This delay in diagnosis reduces treatment success and increases healthcare costs.

## Who it helps

Priya, an ASHA worker in a village outside Erode, Tamil Nadu, is doing her weekly door-to-door visit when a patient shows her an irregular, darkening mole. Priya has no dermatology training and the nearest dermatologist is three hours away. She needs one thing: a fast signal on whether this mole needs urgent referral.

## Solution

DermScanI is an AI-powered skin lesion screening and clinical decision support platform designed to assist a single community health worker like Priya in the early identification of potentially malignant skin lesions.

The application enables users to capture high-quality images of suspicious skin lesions using a smartphone. An image quality assessment module verifies factors such as focus, lighting, and framing before the image is analyzed by a deep learning model. For this hackathon, DermScanI does one thing: Priya photographs a lesion, an image quality check confirms it's usable, and a CNN/ViT model returns one of exactly two outputs — "Refer for review," with the urgency and where to go, or "No flag raised at this time," which always includes what to watch for (change in size, shape, colour, bleeding, or itching) and an explicit way to refer anyway if Priya or the patient is unsure. There is no risk band, no confidence score shown on screen, and no output that reads as a clearance or reassurance. No login, no patient history, no clinical dashboard — just photo in, signal out.

Clinical risk-factor fusion, Grad-CAM explainability, doctor review, longitudinal tracking, and referral routing are part of our long-term vision but are explicitly out of scope for this build — they're listed under Future Roadmap below.
DermScan is designed as a clinical decision support system that assists healthcare professionals in early screening and referral while ensuring that diagnosis and treatment decisions remain under the supervision of qualified medical practitioners.

## Architecture

This begins with the mobile application installed in Priya’s smartphone, from which she takes a photograph of the lesion. The photograph is then subjected to an image quality check, and if it fails, Priya is instructed to retake the photograph rather than processing a poor-quality image. If it passes, the photograph is run through a CNN or ViT classifier, which outputs one of two options: “refer” with the message “irregular pattern detected, please visit the PHC this week,” or “no flag raised at this time” with the message “no urgent pattern detected at this time, but look out for increased size, color changes, bleeding, or itching and visit anyway if you experience any of these or are in doubt.” The result is displayed to Priya in less than 10 seconds. Everything else – clinical risk-factor fusion, Grad-CAM interpretability, physician review pathway, cloud-based storage with longitudinal follow-up, and referral routing – lies ahead on our roadmap and is not being developed as part of the hackathon.
When deploying the system, after the hackathon, Priya will simply install the app directly onto her Android phone using the APK available to her from her ASHA supervisor or PHC coordinator without the need for any app store approval, or access it from our website. The next time she makes a house call and notices a suspicious lesion, she takes out the application, snaps a photo of it and within 10 seconds has the results. What will keep her using it is the speed of it compared to her alternatives of either guessing or waiting a couple weeks for her PHC appointment, and the fact that it does not diagnose anything; it only gives advice.

Note: like most public dermatology datasets, our training data underrepresents darker skin tones - a limitation we'd address with Indian-skin-tone data collection before real-world deployment.

## Tech stack

Frontend: React,Next.js    Backend: FastAPI (Python)      AI: PyTorch, EfficientNet, OpenCV, trained on the HAM10000 (dermoscopic image dataset)     Deployment (hackathon demo): Google Cloud Run       Stretch goals (if time remains): Firebase Storage for result logging, Google Maps API for nearest PHC lookup

## Getting started

1. Accept your collaborator invite (check your email / GitHub notifications).
2. Clone this repo and start building.
3. Commit early and often — this repo is what you present on the day.

---

_Created automatically when your proposal was validated._