import streamlit as st
from inference_sdk import InferenceHTTPClient
import os

# Roboflow API setup
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="fV5LNBhyGxlZQNNZec6W"
)

MODEL_ID = "my-first-project-mdags/1"  # Replace with your actual model ID

# UI
st.set_page_config(page_title="Plant Disease Detector", page_icon="🌿")
st.title("🌿 Plant Disease Detection App")
st.write("Upload a plant image to detect disease using your custom Roboflow model.")

uploaded_file = st.file_uploader("📷 Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_path = "temp.jpg"
    with open(image_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.image(image_path, caption="Uploaded Image", use_column_width=True)

    with st.spinner("🔍 Detecting disease..."):
        try:
            result = CLIENT.infer(image_path, model_id=MODEL_ID)
            os.remove(image_path)  # Clean up

            predictions = result.get("predictions", [])
            if not predictions:
                st.warning("No disease detected.")
            else:
                best = sorted(predictions, key=lambda x: x['confidence'], reverse=True)[0]
                label = best['class']
                confidence = best['confidence']
                st.success(f"✅ **Prediction:** {label}")
                st.info(f"🧪 **Confidence:** {round(confidence * 100, 2)}%")
        except Exception as e:
            st.error(f"❌ Error during prediction: {e}")
