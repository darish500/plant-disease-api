import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import openai

# Set OpenAI API key
openai.api_key = st.secrets["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"]  # or hardcode temporarily

# Language map for translation context
language_prompts = {
    "English": "Respond in clear, simple English.",
    "Yoruba": "Translate and respond in Yoruba language.",
    "Hausa": "Translate and respond in Hausa language.",
    "Igbo": "Translate and respond in Igbo language."
}

# Model configuration and solution mappings
model_configs = {
    "cassava": {
        "model_id": "cassava-disease-zqjxb-rl2r2/1",
        "api_url": "https://serverless.roboflow.com",
        "api_key": "xg0E2Az768qCexdziw72",
        "solutions": {
            "CBB": "Cassava Bacterial Blight: Use resistant varieties.",
            "CMD": "Cassava Mosaic Disease: Remove infected plants.",
            "CGM": "Cassava Green Mite: Apply miticides or use biocontrol.",
            "CBSD": "Cassava Brown Streak Disease: Use virus-free cuttings.",
            "Healthy": "Healthy cassava plant!"
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

def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def detect_image(image, model_id, api_key):
    base64_img = image_to_base64(image)
    url = f"https://detect.roboflow.com/{model_id}?api_key={api_key}&confidence=40"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=base64_img, headers=headers)
    return response.json()

# Streamlit App
st.set_page_config(page_title="Crop AI Doctor", page_icon="🌿")
st.title("🌾 Crop Disease Detector with Chat Assistant")

language = st.selectbox("🌍 Choose Language", list(language_prompts.keys()))
crop = st.selectbox("Select Crop", list(model_configs.keys()))

uploaded_file = st.file_uploader("📤 Upload Crop Image", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("📷 Or take a photo")

input_image = uploaded_file or camera_file
if input_image:
    image = Image.open(input_image).convert("RGB")
    st.image(image, caption="Your Crop", use_column_width=True)

    if st.button("🔍 Detect Disease"):
        st.info("Processing image...")
        config = model_configs[crop]
        result = detect_image(image, config["model_id"], config["api_key"])

        if "predictions" in result and result["predictions"]:
            pred = result["predictions"][0]
            disease = pred["class"]
            solution = config["solutions"].get(disease, "No solution found.")

            st.success(f"🦠 Detected: **{disease}**")
            st.write(f"👉 **Solution**: {solution}")

            # Initialize chat session
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            system_prompt = (
                f"You are an expert crop disease assistant. The plant has **{disease}**.\n"
                f"{language_prompts[language]}"
            )

            for msg in st.session_state.chat_history:
                role = "🧠" if msg["role"] == "assistant" else "🙋"
                st.markdown(f"**{role}**: {msg['content']}")

            user_msg = st.text_input("💬 Ask more about the disease or treatment...")
            if user_msg:
                st.session_state.chat_history.append({"role": "user", "content": user_msg})

                chat_input = [
                    {"role": "system", "content": system_prompt}
                ] + st.session_state.chat_history

                with st.spinner("Thinking..."):
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=chat_input
                    )
                    reply = response.choices[0].message.content
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.experimental_rerun()
        else:
            st.warning("No disease detected. Try another image.")
