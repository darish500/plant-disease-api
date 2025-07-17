import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# ------------------------- Model Configuration -------------------------
model_configs = {
    "cassava": {
        "model_id": "cassava-disease-zqjxb-rl2r2/1",
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

# ------------------------- Translation Dictionary -------------------------
translations = {
    "Yoruba": {
        "Cassava Bacterial Blight: Use resistant varieties.": "Àrùn Bakteria lórí Ewé Ege: Lo irugbin tí ó ní agbára láti koju àrùn.",
        "Cassava Mosaic Disease: Remove infected plants.": "Àrùn Mosaic lórí Ege: Yọ àwọn ohun ọgbin tí àrùn ti kan.",
        "Cassava Green Mite: Apply miticides or use biocontrol.": "Ajẹsara aláwọ ewe ege: Lò òògùn tó pa kokoro tàbí lo ọna àbojútó.",
        "Cassava Brown Streak Disease: Use virus-free cuttings.": "Àrùn yíyọ dudu lórí Ege: Lo ewé tó kò ní kó-rúsì.",
        "Healthy cassava plant!": "Ege rẹ dára, kò ní àrùn!"
        # Add more translations for maize and rice...
    },
    "Hausa": {
        "Cassava Bacterial Blight: Use resistant varieties.": "Cutar Bakteriya ta Kasaba: Yi amfani da irin da ke da kariya.",
        "Cassava Mosaic Disease: Remove infected plants.": "Cutar Mosaic na Kasaba: Cire tsirran da suka kamu da cuta.",
        "Healthy cassava plant!": "Kasaba lafiya lau!"
    },
    "Igbo": {
        "Cassava Bacterial Blight: Use resistant varieties.": "Ọrịa Bakterịa n’akụkụ Cassava: Jiri ụdị nwere mgbochi.",
        "Healthy cassava plant!": "Cassava gị dị mma, enweghị ọrịa!"
    }
}

# ------------------------- Utility Functions -------------------------
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

def translate(text, language):
    return translations.get(language, {}).get(text, text)

# ------------------------- Streamlit UI -------------------------
st.set_page_config(page_title="Crop Disease Detector", layout="centered")
st.title("🌱 AI-Powered Crop Disease Detector")

crop = st.selectbox("Select Crop Type", list(model_configs.keys()))
language = st.selectbox("Select Language", ["English", "Yoruba", "Hausa", "Igbo"])

uploaded_file = st.file_uploader("Upload Crop Image", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("Or Take a Picture")

input_image = None
if uploaded_file:
    input_image = Image.open(uploaded_file).convert("RGB")
elif camera_file:
    input_image = Image.open(camera_file).convert("RGB")

if input_image:
    st.image(input_image, caption="Selected Image", use_column_width=True)

    if st.button("Detect Disease"):
        st.info("Analyzing image, please wait...")
        config = model_configs[crop]
        result = detect_image(input_image, config["model_id"], config["api_key"])

        if "predictions" in result and result["predictions"]:
            st.subheader("🧬 Detected Diseases and Recommendations")
            shown = set()
            for pred in result["predictions"]:
                disease = pred["class"]
                if disease not in shown:
                    shown.add(disease)
                    solution = config["solutions"].get(disease, "No solution available.")
                    st.markdown(f"**{disease}**")
                    st.success(f"{translate(solution, language)}")

            st.markdown("---")
            st.subheader("🤖 Extra Help")
            selected_question = st.selectbox("Choose a question", [
                "What can I do to prevent this disease?",
                "Can I still save my plant?",
                "Should I report this case to local agriculture office?"
            ])

            answers = {
                "What can I do to prevent this disease?": {
                    "English": "You should practice crop rotation, use certified seeds, and ensure good field sanitation.",
                    "Yoruba": "Lo irugbin to dáa, yipada ipo irugbin, ki o si mó ibi tí o gbin mọ́.",
                    "Hausa": "Yi amfani da ingantattun iri, juya tsirrai, da tsabtace gona.",
                    "Igbo": "Jiri mkpụrụ dị mma, gbanwee ebe ị na-akọrọ, na-asacha ubi."
                },
                "Can I still save my plant?": {
                    "English": "If detected early, proper treatment can help the plant recover.",
                    "Yoruba": "Tí o bá mọ̀ ní kákàkiri, ìtọ́jú tó péye lè dáàbò bò ọgbìn.",
                    "Hausa": "Idan an gano da wuri, magani mai kyau na iya ceton tsiron.",
                    "Igbo": "Ọ bụrụ na a matara ya n’oge, ọgwụ ziri ezi nwere ike ịzọpụta ya."
                },
                "Should I report this case to local agriculture office?": {
                    "English": "Yes, especially if it's spreading. They can provide expert help.",
                    "Yoruba": "Bẹẹni, pẹ̀lú pàápàá jùlọ tí àrùn náà bá ń tàn kálẹ̀. Wọ́n lè ràn ẹ́ lọ́wọ́.",
                    "Hausa": "I, musamman idan cutar na yaduwa. Suna da masaniya da taimako.",
                    "Igbo": "Ee, karịsịa ma ọ bụrụ na ọrịa na-agbasa. Ha nwere ike inye aka."
                }
            }

            st.info(answers[selected_question][language])
        else:
            st.warning("No disease detected. Please try another image.")
