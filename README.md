# 🧠 Nasal Polyp Segmentation using Deep Learning

A deep learning-based web application for detecting and segmenting nasal polyps from CT scan images.  
This project provides a user-friendly interface to upload scans and visualize segmentation results in real time.

---

## 🚀 Live Demo

👉 https://huggingface.co/spaces/monikabaabu/Nasal-Polyp-Segmentation

---

## 📌 Features

- Upload CT scan images
- Automatic polyp segmentation using deep learning
- Visualization of:
  - Original Image
  - Segmentation Mask
  - Overlay Output
- Polyp area calculation (in pixels and mm²)
- Multiple model selection 
- Clean and interactive UI

---

## 🧠 Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask
- **Deep Learning:** PyTorch, segmentation-models-pytorch
- **Image Processing:** OpenCV, NumPy
- **Deployment:** Hugging Face Spaces (Docker)

---

## 🏗️ Project Structure

```
Nasal-Polyp-Segmentation/
│
├── app.py
├── Dockerfile
├── requirements.txt
│
├── templates/
│ └── index.html
│
├── static/
│ ├── app.js
│ └── style.css
│
├── models/
│ └── model.pth

```

---

## ⚙️ How It Works

1. User uploads a CT scan image
2. Image is preprocessed and passed to the trained model
3. Model generates a segmentation mask
4. Mask is overlaid on the original image
5. Polyp area is calculated based on segmented pixels

---

## 📊 Area Calculation

The area is computed as:

Area = Number of segmented pixels × (pixel spacing)²

> Note: If pixel spacing is not available, area is approximated using pixel count.

---

## 🧪 Run Locally

```bash
git clone https://github.com/monikabaabu/Nasal-Polyp-Segmentation.git
cd Nasal-Polyp-Segmentation

pip install -r requirements.txt
python app.py
