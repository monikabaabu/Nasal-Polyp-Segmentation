# app.py
from flask import Flask, request, jsonify, render_template
import torch
import segmentation_models_pytorch as smp
import cv2
import numpy as np
import base64
from PIL import Image
import io
import os

app = Flask(__name__)

# ── device ────────────────────────────────────────────────────────
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# ── load all 5 models ─────────────────────────────────────────────
def load_model(architecture, weights_path):
    if architecture == 'unet':
        model = smp.Unet(encoder_name='resnet34', encoder_weights=None,
                         in_channels=3, classes=1, activation=None)
    elif architecture == 'segnet':
        model = smp.Linknet(encoder_name='resnet34', encoder_weights=None,
                            in_channels=3, classes=1, activation=None)
    elif architecture == 'deeplab':
        model = smp.DeepLabV3Plus(encoder_name='resnet34', encoder_weights=None,
                                  in_channels=3, classes=1, activation=None)
    elif architecture == 'manet':
        model = smp.MAnet(encoder_name='resnet34', encoder_weights=None,
                          in_channels=3, classes=1, activation=None)
    elif architecture == 'unet3plus':
        model = smp.UnetPlusPlus(encoder_name='resnet34', encoder_weights=None,
                                 in_channels=3, classes=1, activation=None)

    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()
    model.to(device)
    return model

# ── model paths ───────────────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

print("Loading models...")
models = {
    'U-Net'      : load_model('unet',     os.path.join(MODEL_DIR, 'best_model.pth')),
    'SegNet'     : load_model('segnet',   os.path.join(MODEL_DIR, 'best_segnet_model.pth')),
    'DeepLabV3+' : load_model('deeplab',  os.path.join(MODEL_DIR, 'best_deeplab_model.pth')),
    'MAnet'      : load_model('manet',    os.path.join(MODEL_DIR, 'best_manet_model.pth')),
    'UNet3+'     : load_model('unet3plus',os.path.join(MODEL_DIR, 'best_unet3plus_model.pth')),
}
print("✅ All models loaded!")

# ── prediction function ───────────────────────────────────────────
def predict(image_bytes, model_name):
    # read image
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = np.array(img)
    img_resized = cv2.resize(img, (256, 256))

    # preprocess
    img_tensor = torch.from_numpy(
        img_resized.astype(np.float32) / 255.0
    ).permute(2, 0, 1).unsqueeze(0).to(device)

    # predict
    with torch.no_grad():
        pred = torch.sigmoid(models[model_name](img_tensor))
        pred_binary = (pred > 0.5).squeeze().cpu().numpy().astype(np.float32)

    # build overlay
    overlay = img_resized.copy().astype(np.float32) / 255.0
    overlay[pred_binary == 1, 0] = 1.0
    overlay[pred_binary == 1, 1] *= 0.3
    overlay[pred_binary == 1, 2] *= 0.3
    blended = cv2.addWeighted(img_resized.astype(np.float32)/255.0,
                               0.6, overlay, 0.4, 0)

    # draw contour
    pred_uint8  = (pred_binary * 255).astype(np.uint8)
    contours, _ = cv2.findContours(pred_uint8, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    blended_uint8 = (blended * 255).astype(np.uint8)
    cv2.drawContours(blended_uint8, contours, -1, (0, 255, 0), 1)

    # polyp size
    polyp_pixels = int(pred_binary.sum())
    pixel_size_mm = 0.5  # approximate CT pixel spacing
    polyp_area_mm2 = polyp_pixels * (pixel_size_mm ** 2)

    # severity
    if polyp_area_mm2 < 100:
        severity = "Grade 1 — Small (Monitor)"
        severity_color = "green"
    elif polyp_area_mm2 < 500:
        severity = "Grade 2 — Medium (Medication)"
        severity_color = "orange"
    else:
        severity = "Grade 3 — Large (Surgery)"
        severity_color = "red"

    # convert to base64
    _, buffer = cv2.imencode('.png', blended_uint8)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    _, buffer2 = cv2.imencode('.png', pred_uint8)
    mask_base64 = base64.b64encode(buffer2).decode('utf-8')

    return {
        'overlay'       : img_base64,
        'mask'          : mask_base64,
        'polyp_pixels'  : polyp_pixels,
        'polyp_area_mm2': round(polyp_area_mm2, 2),
        'severity'      : severity,
        'severity_color': severity_color,
    }

# ── routes ────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file       = request.files['file']
    model_name = request.form.get('model', 'UNet3+')

    result = predict(file.read(), model_name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860)