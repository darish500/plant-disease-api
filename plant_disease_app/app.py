import streamlit as st
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import base64

# Model configuration and solution mappings
model_configs = {
    "cassava": {
        "model_id": "cassava-disease-zqjxb-rl2r2/1",
        "api_url": "https://serverless.roboflow.com",  # or detect.roboflow.com
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
    }
    ,
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

# Convert uploaded image to base64
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# Perform inference
def detect_image(image, model_id, api_key):
    base64_img = image_to_base64(image)
    url = f"https://detect.roboflow.com/{model_id}?api_key={api_key}&confidence=40"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=base64_img, headers=headers)
    return response.json()

# Draw bounding boxes on image
# def draw_detections(image, predictions):
#     draw = ImageDraw.Draw(image)
#     for pred in predictions:
#         x, y, w, h = pred['x'], pred['y'], pred['width'], pred['height']
#         left = x - w / 2
#         top = y - h / 2
#         right = x + w / 2
#         bottom = y + h / 2
#         label = f"{pred['class']} ({int(pred['confidence'] * 100)}%)"
#         draw.rectangle([left, top, right, bottom], outline="red", width=3)
#         draw.text((left, top - 10), label, fill="red")
#     return image

# Streamlit UI
st.title("🌾 AI-Powered Crop Disease Detector")
crop = st.selectbox("Select Crop", list(model_configs.keys()))
uploaded_file = st.file_uploader("Upload Crop Image", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("Take a picture")
# Use either upload or camera
input_image = None
if uploaded_file:
    input_image = Image.open(uploaded_file).convert("RGB")
elif camera_file:
    input_image = Image.open(camera_file).convert("RGB")

if input_image:
    st.image(input_image, caption="Selected Image", use_column_width=True)

    if st.button("Detect Disease"):
        st.info("Processing...")
        config = model_configs[crop]
        result = detect_image(input_image, config["model_id"], config["api_key"])

        if "predictions" in result and result["predictions"]:
            predictions = result["predictions"]
            # detected_image = draw_detections(image.copy(), predictions)
            # st.image(detected_image, caption="Detection Result", use_column_width=True)

            st.subheader("🦠 Detected Diseases and Solutions")
            shown_classes = set()
            for pred in predictions:
                disease = pred["class"]
                if disease not in shown_classes:
                    shown_classes.add(disease)
                    solution = config["solutions"].get(disease, "No solution available.")
                    st.markdown(f"**{disease}**")
                    st.write(f"👉 Solution: {solution}")
                    st.info("Done")
        else:
            st.warning("No disease detected.")
import openai

# Initialize OpenAI
openai.api_key = API_KEYS["openai"]

# Optional: Language selection
lang = st.selectbox("Select Language", ["English", "French", "Yoruba", "Hausa"])

# Convert language to prompt
lang_prompts = {
    "English": "Respond in English.",
    "French": "Répondez en français.",
    "Yoruba": "Jọwọ dahun ni Yoruba.",
    "Hausa": "Don Allah, amsa da Hausa."
}

if st.checkbox("💬 Ask the AI assistant about the disease"):
    user_query = st.text_input("Enter your question")

    if user_query:
        prompt = f"""
        You are an AI agricultural assistant.
        The user uploaded a plant image and detected this disease: {', '.join(shown_classes)}.

        {lang_prompts[lang]}

        Question: {user_query}
        """

        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(f"**🧠 AI Response:** {response['choices'][0]['message']['content']}")
            except Exception as e:
                st.error("Something went wrong with OpenAI API.")
