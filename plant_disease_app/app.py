# streamlit_crop_disease_app.py
import streamlit as st
from inference_sdk import InferenceHTTPClient
import cv2
import numpy as np
from PIL import Image
import tempfile

# === Custom CSS Styling ===
st.markdown("""
    <style>
        body {
            background-color: #f0f8ff;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2b7a78;
            text-align: center;
            font-family: 'Trebuchet MS', sans-serif;
        }
        .uploadedImage {
            border: 2px solid #2b7a78;
            border-radius: 10px;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .prediction {
            background-color: #e0f7fa;
            padding: 10px;
            border-left: 5px solid #00796b;
            margin-bottom: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""<h1>🌿 Plant Disease Detection App</h1>""", unsafe_allow_html=True)

# === Model Definitions ===
models = {
    "cassava": {
        "model_id": "cassava-disease-zqjxb-rl2r2/1",
        "api_url": "https://serverless.roboflow.com",
        "api_key": "xg0E2Az768qCexdziw72",
        "solutions": {
            "cbb": "Cassava Bacterial Blight: Use resistant varieties.",
            "cmd": "Cassava Mosaic Disease: Remove infected plants.",
            "cgm": "Cassava Green Mite: Apply miticides or use biocontrol.",
            "cbsd": "Cassava Brown Streak Disease: Use virus-free cuttings.",
            "healthy": "Healthy cassava plant!"
        }
    },
    "maize": {
        "model_id": "maize-disease-w9ggw/2",
        "api_url": "https://serverless.roboflow.com",
        "api_key": "HjAbvCwdDSoHCJzZBFIR",
        "solutions": {
            "Anthracnose_leaf_blight": "Remove infected debris and rotate crops.",
            "Bactarial_leaf_streak_of_corn": "Use disease-free seeds and resistant hybrids.",
            "Banded_leaf_and_sheath_blight": "Avoid waterlogging and use recommended fungicides.",
            "Brown_spot": "Apply nitrogen-rich fertilizers and ensure good drainage.",
            "Common_rust": "Use resistant varieties and apply fungicides if needed.",
            "Fall_Armyworm": "Apply biopesticides or neem-based products; monitor regularly.",
            "Gray_leaf_spot": "Rotate crops, avoid high planting density.",
            "Northern_leaf_blight": "Use fungicide and resistant seed varieties.",
            "Southern_leaf_Blight": "Practice crop rotation and ensure clean field management."
        }
    },
    "rice": {
        "model_id": "rice-disease-vahwz-6b2ii/1",
        "api_url": "https://serverless.roboflow.com",
        "api_key": "HjAbvCwdDSoHCJzZBFIR",
        "solutions": {
            "Bacterial Leaf Blight Disease or Bacterial Blight Disease": "Use certified seeds and avoid excessive nitrogen.",
            "Bacterial Leaf Streak Disease": "Plant resistant varieties and use appropriate field sanitation.",
            "Brown Spot Disease": "Apply potash fertilizers and practice good water management.",
            "Dirty Panicle Disease": "Ensure clean seeds and use fungicides before heading.",
            "Grassy Stunt Disease": "Control brown planthopper and use resistant varieties.",
            "Narrow Brown Spot Disease": "Manage nitrogen levels and improve drainage.",
            "Rice Blast Disease": "Apply balanced fertilizers and use fungicides when necessary.",
            "Rice Ragged Stunt Disease": "Control vectors like brown planthopper; remove infected plants.",
            "Rice Tungro Disease or Yellow Orange Leaf Disease": "Use vector-resistant rice and early planting.",
            "Sheath blight Disease": "Avoid dense planting and use resistant rice strains."
        }
    }
}

# === UI for Crop and Image Upload ===
crop = st.selectbox("Select Crop Type", ["cassava", "maize", "rice"])
uploaded_file = st.file_uploader("Upload a crop leaf image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp_path = tmp.name
        image.save(tmp_path)

    st.markdown('<div class="uploadedImage">', unsafe_allow_html=True)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    model_info = models[crop]
    client = InferenceHTTPClient(
        api_url=model_info["api_url"],
        api_key=model_info["api_key"]
    )

    result = client.infer(tmp_path, model_id=model_info["model_id"])
    predictions = result["predictions"]

    if predictions:
        for pred in predictions:
            label = pred["class"]
            solution = model_info["solutions"].get(label, "No solution available.")
            confidence = pred.get("confidence", 0.0)

            st.markdown(f"""
                <div class='prediction'>
                    <b>🦠 {label}</b> — Confidence: {confidence:.2f}<br>
                    <b>💡 Solution:</b> {solution}
                </div>
            """, unsafe_allow_html=True)

            if all(k in pred for k in ["x", "y", "width", "height"]):
                x1 = int(pred["x"] - pred["width"] / 2)
                y1 = int(pred["y"] - pred["height"] / 2)
                x2 = int(pred["x"] + pred["width"] / 2)
                y2 = int(pred["y"] + pred["height"] / 2)

                cv2.rectangle(img_array, (x1, y1), (x2, y2), (255, 0, 0), 2)
                label_text = f"{label}: {confidence:.2f}"
                cv2.putText(img_array, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        st.image(img_array, caption="Predictions on Image", use_column_width=True)
    else:
        st.success("✅ No issue detected. Healthy crop!")
        st.image(image, caption="Original Image (Healthy)", use_column_width=True)
