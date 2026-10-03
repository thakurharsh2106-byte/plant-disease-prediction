import os
import sys
import uuid
import numpy as np
import pandas as pd
from PIL import Image
import torch
import torchvision.transforms.functional as TF
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, request, jsonify, url_for

# Ensure current directory is in sys.path for CNN import
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import CNN

# Setup upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Resolve CSV paths
disease_csv_path = os.path.join(BASE_DIR, 'disease_info.csv')
supplement_csv_path = os.path.join(BASE_DIR, 'supplement_info.csv')

disease_info = pd.read_csv(disease_csv_path, encoding='cp1252')
supplement_info = pd.read_csv(supplement_csv_path, encoding='cp1252')

# Resolve Model Weights path
model_candidates = [
    os.path.join(BASE_DIR, 'plant_disease_model_1_latest.pt'),
    os.path.join(BASE_DIR, '..', 'Plant Disease Model', 'plant_disease_model_1_latest.pt'),
    os.path.join(BASE_DIR, '..', 'plant_disease_model_1_latest.pt')
]

model_path = None
for candidate in model_candidates:
    if os.path.exists(candidate):
        model_path = candidate
        break

if not model_path:
    print(f"Warning: Model weights file not found in candidates: {model_candidates}")
    model = None
else:
    print(f"Loading PyTorch CNN model from: {model_path}")
    model = CNN.CNN(39)
    device = torch.device('cpu')
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print("Model loaded successfully into memory.")

HEALTHY_INDICES = {3, 5, 7, 11, 15, 18, 20, 23, 24, 25, 28, 38}

def parse_steps(steps_text):
    if not isinstance(steps_text, str) or not steps_text.strip():
        return []
    lines = [line.strip() for line in steps_text.replace('\r', '').split('\n') if line.strip()]
    cleaned = []
    for line in lines:
        # Strip leading numbers or bullets if present
        trimmed = line.lstrip('0123456789.-•* ')
        if trimmed:
            cleaned.append(trimmed)
    return cleaned if cleaned else [steps_text.strip()]

def predict_image(image_path):
    if model is None:
        raise RuntimeError("Model is not initialized.")

    image = Image.open(image_path).convert('RGB')
    image = image.resize((224, 224))
    input_tensor = TF.to_tensor(image).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)[0]
        top_confs, top_indices = torch.topk(probs, 3)

    pred_idx = top_indices[0].item()
    confidence = round(top_confs[0].item() * 100, 2)

    top_3 = []
    for conf, idx in zip(top_confs, top_indices):
        c_idx = idx.item()
        c_name = disease_info['disease_name'][c_idx] if c_idx < len(disease_info) else CNN.idx_to_classes.get(c_idx, 'Unknown')
        top_3.append({
            'index': c_idx,
            'name': c_name,
            'confidence': round(conf.item() * 100, 2)
        })

    # Status determination
    if pred_idx == 4:
        status = 'no_leaf'
    elif pred_idx in HEALTHY_INDICES:
        status = 'healthy'
    else:
        status = 'diseased'

    title = disease_info['disease_name'][pred_idx]
    desc = disease_info['description'][pred_idx] if pd.notna(disease_info['description'][pred_idx]) else 'No description available.'
    raw_steps = disease_info['Possible Steps'][pred_idx] if pd.notna(disease_info['Possible Steps'][pred_idx]) else ''
    prevent_steps = parse_steps(raw_steps)
    image_url = disease_info['image_url'][pred_idx] if pd.notna(disease_info['image_url'][pred_idx]) else ''

    # Supplement info
    sname = supplement_info['supplement name'][pred_idx] if pd.notna(supplement_info['supplement name'][pred_idx]) else ''
    simage = supplement_info['supplement image'][pred_idx] if pd.notna(supplement_info['supplement image'][pred_idx]) else ''
    buy_link = supplement_info['buy link'][pred_idx] if pd.notna(supplement_info['buy link'][pred_idx]) else ''

    # Extract crop name
    crop = title.split(':')[0].strip() if ':' in title else 'Crop'

    return {
        'pred': pred_idx,
        'title': title,
        'crop': crop,
        'status': status,
        'confidence': confidence,
        'desc': desc,
        'prevent_steps': prevent_steps,
        'image_url': image_url,
        'sname': sname,
        'simage': simage,
        'buy_link': buy_link,
        'top_3': top_3
    }

# Flask Application
app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Crops data for homepage
CROPS_CATALOG = [
    {'name': 'Apple', 'diseases': 'Scab, Black Rot, Cedar Rust', 'img': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Tomato', 'diseases': 'Bacterial Spot, Blights, Leaf Mold, Mosaic', 'img': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Corn (Maize)', 'diseases': 'Rust, Northern Leaf Blight, Gray Spot', 'img': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Potato', 'diseases': 'Early Blight, Late Blight', 'img': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Grape', 'diseases': 'Black Rot, Esca, Leaf Blight', 'img': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Pepper Bell', 'diseases': 'Bacterial Spot', 'img': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Strawberry', 'diseases': 'Leaf Scorch', 'img': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Cherry', 'diseases': 'Powdery Mildew', 'img': 'https://images.unsplash.com/photo-1528825871115-3581a5387919?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Peach', 'diseases': 'Bacterial Spot', 'img': 'https://images.unsplash.com/photo-1629828874514-c1e5103f2150?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Orange (Citrus)', 'diseases': 'Huanglongbing (Greening)', 'img': 'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Blueberry', 'diseases': 'Health Screening', 'img': 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=300&auto=format&fit=crop&q=80'},
    {'name': 'Soybean', 'diseases': 'Foliar Screening', 'img': 'https://images.unsplash.com/photo-1599582909641-655f247926e2?w=300&auto=format&fit=crop&q=80'},
]

# Curated test samples for quick testing in AI Studio
def get_sample_chips():
    samples_dir = os.path.join(BASE_DIR, 'static', 'test_samples')
    chips = []
    sample_files = [
        ('Apple_ceder_apple_rust.JPG', 'Apple: Cedar Rust', 'Apple'),
        ('tomato_early_blight.JPG', 'Tomato: Early Blight', 'Tomato'),
        ('corn_common_rust.JPG', 'Corn: Common Rust', 'Corn'),
        ('potato_early_blight.JPG', 'Potato: Early Blight', 'Potato'),
        ('grape_black_rot.JPG', 'Grape: Black Rot', 'Grape'),
        ('apple_healthy.JPG', 'Apple: Healthy', 'Apple'),
        ('tomato_yellow_leaf_curl_virus.JPG', 'Tomato: Yellow Curl', 'Tomato'),
        ('background_without_leaves.jpg', 'Non-Leaf Photo', 'Background')
    ]
    for filename, label, crop in sample_files:
        filepath = os.path.join(samples_dir, filename)
        if os.path.exists(filepath):
            chips.append({
                'filename': filename,
                'label': label,
                'crop': crop,
                'url': f'/static/test_samples/{filename}'
            })
    return chips

# ==========================================================================
# Web Routes
# ==========================================================================
@app.route('/')
def home():
    return render_template('home.html', crops=CROPS_CATALOG)

@app.route('/index')
@app.route('/diagnose')
def ai_engine_page():
    samples = get_sample_chips()
    return render_template('index.html', samples=samples)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'GET':
        # Allow testing via sample query parameter
        sample = request.args.get('sample')
        if sample:
            sample_path = os.path.join(BASE_DIR, 'static', 'test_samples', secure_filename(sample))
            if os.path.exists(sample_path):
                result = predict_image(sample_path)
                result['user_image'] = f'/static/test_samples/{sample}'
                return render_template('submit.html', **result)
        return redirect(url_for('ai_engine_page'))

    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(url_for('ai_engine_page'))
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(url_for('ai_engine_page'))

        clean_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"leaf_{uuid.uuid4().hex[:10]}.{clean_ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)

        result = predict_image(save_path)
        result['user_image'] = f'/static/uploads/{unique_name}'
        return render_template('submit.html', **result)

@app.route('/market')
def market():
    products = []
    for idx, row in supplement_info.iterrows():
        if idx == 4:  # Skip background without leaves
            continue
        disease_name = disease_info['disease_name'][idx]
        plant = disease_name.split(':')[0].strip() if ':' in disease_name else disease_name
        is_healthy = idx in HEALTHY_INDICES
        category = 'healthy' if is_healthy else 'diseased'

        sname = str(row['supplement name']) if pd.notna(row['supplement name']) else 'Recommended Organic Care'
        simage = str(row['supplement image']) if pd.notna(row['supplement image']) else 'https://cdn-icons-png.flaticon.com/512/628/628324.png'
        buy_link = str(row['buy link']) if pd.notna(row['buy link']) and str(row['buy link']).startswith('http') else '#'

        products.append({
            'index': idx,
            'plant': plant,
            'disease': disease_name,
            'name': sname,
            'image': simage,
            'buy_link': buy_link,
            'category': category,
            'is_healthy': is_healthy
        })
    return render_template('market.html', products=products)

@app.route('/encyclopedia')
def encyclopedia():
    entries = []
    unique_crops = set()
    for idx, row in disease_info.iterrows():
        title = row['disease_name']
        crop = title.split(':')[0].strip() if ':' in title else title
        if idx != 4:
            unique_crops.add(crop)

        is_healthy = idx in HEALTHY_INDICES
        status = 'no_leaf' if idx == 4 else ('healthy' if is_healthy else 'diseased')
        steps = parse_steps(row['Possible Steps']) if pd.notna(row['Possible Steps']) else []
        desc = row['description'] if pd.notna(row['description']) else ''
        img = row['image_url'] if pd.notna(row['image_url']) else ''

        sname = supplement_info.loc[idx, 'supplement name'] if idx in supplement_info.index and pd.notna(supplement_info.loc[idx, 'supplement name']) else ''
        buy_link = supplement_info.loc[idx, 'buy link'] if idx in supplement_info.index and pd.notna(supplement_info.loc[idx, 'buy link']) else ''

        entries.append({
            'index': idx,
            'title': title,
            'crop': crop,
            'status': status,
            'description': desc,
            'steps': steps,
            'image_url': img,
            'supplement': sname,
            'buy_link': buy_link
        })
    return render_template('encyclopedia.html', entries=entries, crops=sorted(list(unique_crops)))

@app.route('/contact')
def contact():
    return render_template('contact-us.html')

# ==========================================================================
# REST API Endpoints
# ==========================================================================
@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'pytorch_version': torch.__version__,
        'classes_count': len(disease_info),
        'device': 'cpu'
    })

@app.route('/api/diseases', methods=['GET'])
def api_diseases():
    result = []
    for idx, row in disease_info.iterrows():
        result.append({
            'index': int(idx),
            'disease_name': row['disease_name'],
            'description': row['description'] if pd.notna(row['description']) else '',
            'is_healthy': idx in HEALTHY_INDICES,
            'image_url': row['image_url'] if pd.notna(row['image_url']) else ''
        })
    return jsonify({'success': True, 'count': len(result), 'diseases': result})

@app.route('/api/predict', methods=['POST'])
def api_predict():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided in request.'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid or unsupported image file format.'}), 400

    clean_ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"api_leaf_{uuid.uuid4().hex[:10]}.{clean_ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(save_path)

    try:
        pred_data = predict_image(save_path)
        pred_data['success'] = True
        return jsonify(pred_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_port():
    env_port = os.environ.get('PORT')
    if env_port:
        return int(env_port)
    return 5001

if __name__ == '__main__':
    port = get_port()
    print("=" * 60)
    print(" 🌿 PlantGuard AI - Plant Disease Prediction System")
    print(f" 🚀 Running on: http://127.0.0.1:{port}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
