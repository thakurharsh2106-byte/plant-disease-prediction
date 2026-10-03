# 🌿 PlantGuard AI - Plant Disease Prediction System

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717.svg?logo=github)](https://github.com/thakurharsh2106-byte/plant-disease-prediction)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Flask 2.2+](https://img.shields.io/badge/Flask-2.2+-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Accuracy](https://img.shields.io/badge/Test%20Accuracy-99.2%25-brightgreen.svg)](https://github.com/thakurharsh2106-byte/plant-disease-prediction)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**PlantGuard AI** is an end-to-end deep learning system and web application designed to help farmers, agronomists, and home gardeners detect and diagnose foliar plant diseases instantly. Powered by an 8-layer Convolutional Neural Network (CNN) built in PyTorch and trained on the PlantVillage dataset, the model identifies **38 distinct plant conditions across 14 vital crop families**, plus an automatic background/non-leaf rejection filter.

---

## 🌟 Key Features

- **⚡ Instant 99.2% Accurate Diagnosis**: Millisecond deep-learning inference with softmax confidence scores and Top-3 candidate probability breakdowns.
- **📸 Dual Input Methods**: Drag-and-drop file upload (JPG, PNG, WebP) or **Live Camera Stream** with real-time video preview and snapshot capture directly in the browser.
- **💡 1-Click Interactive Demo Samples**: Pre-loaded test leaf specimens directly in the UI for instant testing without needing photos on your computer.
- **🔬 Side-by-Side Clinical Inspection**: Compares user-uploaded specimens directly with high-resolution reference samples from the PlantVillage dataset.
- **📋 Actionable Treatment Protocols**: Formatted prevention steps, cultural practices, and biological controls for every condition.
- **🛒 Agricultural Input Marketplace**: Curated catalog of systemic fungicides, bactericides, and micronutrient plant boosters with direct purchase links.
- **📚 Plant Disease Encyclopedia**: Comprehensive searchable directory of all 38 diseases and healthy crop profiles.
- **🔌 Full REST API (`/api/predict`)**: JSON endpoints for seamless integration with mobile apps, drone imaging pipelines, or IoT farm monitoring systems.
- **📱 100% Mobile & Tablet Responsive**: Modern eco-tech design system built with custom CSS, glassmorphism, and responsive grid layouts.
- **🖨️ Printable Pathology Reports**: Built-in print stylesheets to export clinical diagnostic sheets for field reference or records.

---

## 🌾 Supported Crops & Diseases (39 Classes)

| Crop Family | Conditions Detected |
|---|---|
| **Apple** | Apple Scab, Black Rot, Cedar Apple Rust, Healthy |
| **Blueberry** | Healthy |
| **Cherry** | Powdery Mildew, Healthy |
| **Corn (Maize)** | Cercospora Leaf Spot / Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy |
| **Grape** | Black Rot, Esca (Black Measles), Leaf Blight (Isariopsis), Healthy |
| **Orange** | Huanglongbing (Citrus Greening) |
| **Peach** | Bacterial Spot, Healthy |
| **Pepper Bell** | Bacterial Spot, Healthy |
| **Potato** | Early Blight, Late Blight, Healthy |
| **Raspberry** | Healthy |
| **Soybean** | Healthy |
| **Squash** | Powdery Mildew |
| **Strawberry** | Leaf Scorch, Healthy |
| **Tomato** | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites (Two-Spotted), Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy |
| **Background** | Rejection filter for non-plant/non-leaf images |

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/thakurharsh2106-byte/plant-disease-prediction.git
cd plant-disease-prediction
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
You can run the application directly from the root project directory:
```bash
python run.py
```
*Alternatively, you can run `python app.py` or `python wsgi.py`.*

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔌 REST API Documentation

### 1. Model Health Check
**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "pytorch_version": "2.14.1",
  "classes_count": 39,
  "device": "cpu"
}
```

### 2. Predict Leaf Disease
**Endpoint**: `POST /api/predict`  
**Content-Type**: `multipart/form-data`  
**Parameter**: `image` (binary file)

**Example cURL**:
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -F "image=@test_images/Apple_ceder_apple_rust.JPG"
```

**Response**:
```json
{
  "success": true,
  "crop": "Apple",
  "title": "Apple : Cedar rust",
  "status": "diseased",
  "confidence": 99.99,
  "top_3": [
    { "index": 2, "name": "Apple : Cedar rust", "confidence": 99.99 },
    { "index": 6, "name": "Cherry : Powdery Mildew", "confidence": 0.01 },
    { "index": 29, "name": "Tomato : Bacterial Spot", "confidence": 0.00 }
  ],
  "desc": "Cedar apple rust is caused by the fungus Gymnosporangium juniperi-virginianae...",
  "prevent_steps": [
    "Remove galls from infected junipers during late winter/early spring.",
    "Apply preventative fungicides at pink bud stage through petal fall.",
    "Plant rust-resistant apple cultivars when establishing new plantings."
  ],
  "sname": "Spectracide Immunox Multi-Purpose Fungicide",
  "buy_link": "https://..."
}
```

### 3. List All Diseases & Metadata
**Endpoint**: `GET /api/diseases`

---

## 🧠 Neural Network Architecture

The deep learning model is an 8-convolutional layer CNN implemented in PyTorch:

```
Input Image (3 x 224 x 224 RGB)
  │
  ├─ ConvBlock 1: Conv2D(3 -> 32) -> ReLU -> BatchNorm2D(32) -> Conv2D(32 -> 32) -> ReLU -> BatchNorm2D(32) -> MaxPool(2x2)
  │
  ├─ ConvBlock 2: Conv2D(32 -> 64) -> ReLU -> BatchNorm2D(64) -> Conv2D(64 -> 64) -> ReLU -> BatchNorm2D(64) -> MaxPool(2x2)
  │
  ├─ ConvBlock 3: Conv2D(64 -> 128) -> ReLU -> BatchNorm2D(128) -> Conv2D(128 -> 128) -> ReLU -> BatchNorm2D(128) -> MaxPool(2x2)
  │
  ├─ ConvBlock 4: Conv2D(128 -> 256) -> ReLU -> BatchNorm2D(256) -> Conv2D(256 -> 256) -> ReLU -> BatchNorm2D(256) -> MaxPool(2x2)
  │
  ├─ Spatial Flatten (256 * 14 * 14 = 50,176 dimensions)
  │
  ├─ Dense Layer: Linear(50176 -> 1024) -> ReLU -> Dropout(p = 0.4)
  │
  └─ Classification Head: Linear(1024 -> 39) -> Softmax Probabilities
```

---

## 📁 Repository Structure

```
plant-disease-prediction/
├── app.py                       # Root application launcher
├── run.py                       # Alternative root runner
├── wsgi.py                      # WSGI entrypoint for production servers (Gunicorn/uWSGI)
├── download_model.py            # Automated PyTorch weights downloader & validator
├── requirements.txt             # Modern Python dependencies
├── README.md                    # Project documentation
│
├── Flask Deployed App/
│   ├── app.py                   # Production Flask application & API routes
│   ├── CNN.py                   # PyTorch CNN model class definition
│   ├── disease_info.csv         # 39 disease descriptions and treatment steps
│   ├── supplement_info.csv      # Agricultural inputs and product links
│   ├── plant_disease_model_1_latest.pt # Pre-trained 201MB PyTorch model weights
│   ├── requirements.txt         # App-specific dependencies
│   ├── static/
│   │   ├── css/style.css        # Eco-tech design system & animations
│   │   ├── js/main.js           # Drag-drop, camera stream, search & filter
│   │   ├── test_samples/        # Pre-loaded demo leaves for 1-click testing
│   │   └── uploads/             # Temp storage for user uploads
│   └── templates/
│       ├── base.html            # Master layout with responsive navbar & footer
│       ├── home.html            # Modern landing page with crop showcase
│       ├── index.html           # AI diagnosis studio with live webcam & samples
│       ├── submit.html          # Clinical report with side-by-side inspection
│       ├── market.html          # Responsive agricultural inputs marketplace
│       ├── encyclopedia.html    # 38-class plant pathology knowledge base
│       └── contact-us.html      # Architecture and contact form
│
├── Plant Disease Model/
│   └── plant_disease_model_1_latest.pt # Primary weight storage
├── test_images/                 # 44 verified leaf test images
└── Model/                       # Training notebooks, PDFs, and documentation
```

---

## 👤 Author & Maintainer

- **Harsh Vardhan Singh** ([@thakurharsh2106-byte](https://github.com/thakurharsh2106-byte)) — Deep Learning & Web Developer

---

## 📄 License
This project is open-source under the [MIT License](https://opensource.org/licenses/MIT).
