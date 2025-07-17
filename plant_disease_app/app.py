import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# Define supported languages and translations
language_options = {
    "English": "en",
    "Hausa": "ha",
    "Yoruba": "yo",
    "Igbo": "ig"
}

# Example translation dictionaries (expand as needed)
translation_dict = {
    "Fall_Armyworm": {
        "ha": "Dangiya mai kashe amfanin gona",
        "yo": "Kokoro iparun eso",
        "ig": "Nwanyi oku na-akpata ọnwụ mkpụrụ osisi"
    },
    "Apply biopesticides or neem-based products; monitor regularly.": {
        "ha": "Yi amfani da magungunan kashe kwari na halitta ko na neem; duba akai-akai.",
        "yo": "Lo awọn oloro kokoro adayeba tabi awọn ọja neem; ṣọra nigbagbogbo.",
        "ig": "Tinye ọgwụ nje anụmanụ ma ọ bụ ngwaahịa neem; na-enyocha mgbe niile."
    },
    "Can this disease affect yield?": {
        "ha": "Shin wannan cutar na iya rage yawan amfanin gona?",
        "yo": "Ṣe arun yii le ni ipa lori ikore?",
        "ig": "Enwere ike ka ọrịa a metụta mkpokọta?"
    },
    "Yes, this disease significantly reduces crop yield if not managed properly.": {
        "ha": "Eh, wannan cutar na rage yawan amfanin gona idan ba a kula da ita ba.",
        "yo": "Bẹẹni, arun yii dinku ikore to ba jẹ pe a ko tọju rẹ daradara.",
        "ig": "Ee, ọrịa a na-ebelata mkpokọta ma ọ bụrụ na a naghị ewere ya n’isi."
    }
}

# Inbuilt chatbot questions and answers
qa_bank = {
    "Can this disease affect yield?": "Yes, this disease significantly reduces crop yield if not managed properly.",
    "What are the early symptoms?": "Look for leaf discoloration, spots, or unusual patterns.",
    "How do I prevent this disease?": "Use resistant varieties, rotate crops, and monitor plants closely."
}

# Model configurations
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

# Utility functions
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

def translate(text, lang_code):
    return translation_dict.get(text, {}).get(lang_code, text)

# Streamlit UI
st.title("🌾 AI-Powered Crop Disease Detector")
crop = st.selectbox("Select Crop", list(model_configs.keys()))
language = st.selectbox("Select Language", list(language_options.keys()))
lang_code = language_options[language]

uploaded_file = st.file_uploader("Upload Crop Image", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("Take a picture")

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
            st.subheader("🦠 Detected Diseases and Solutions")
            shown_classes = set()
            for pred in result["predictions"]:
                disease = pred["class"]
                if disease not in shown_classes:
                    shown_classes.add(disease)
                    translated_disease = translate(disease, lang_code)
                    solution = config["solutions"].get(disease, "No solution available.")
                    translated_solution = translate(solution, lang_code)
                    st.markdown(f"**{translated_disease}**")
                    st.write(f"👉 Solution: {translated_solution}")

            # Chatbot section
            st.subheader("🤖 Ask a Question about the Detected Disease")
            question = st.selectbox("Choose a question", list(qa_bank.keys()))
            if question:
                translated_q = translate(question, lang_code)
                translated_a = translate(qa_bank[question], lang_code)
                st.markdown(f"**{translated_q}**")
                st.write(f"💬 {translated_a}")
        else:
            st.warning("No disease detected.")
