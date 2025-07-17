import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# ================= SESSION STATE INIT =====================
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'selected_crop' not in st.session_state:
    st.session_state.selected_crop = None
if 'selected_lang' not in st.session_state:
    st.session_state.selected_lang = "English"

# ================= LANGUAGE TRANSLATIONS =====================
language_options = ["English", "Yoruba", "Hausa", "Igbo"]

translations = {
    "English": {},
    "Yoruba": {
        "Cassava Bacterial Blight: Use resistant varieties.": "Aisan kokoro lori ege: Lo irugbin ti o ni idaabobo.",
        "Cassava Mosaic Disease: Remove infected plants.": "Arun aworan ege: Yọ eweko to ni arun kuro.",
        "Cassava Green Mite: Apply miticides or use biocontrol.": "Abo alawọ ewe lori ege: Lo oogun kokoro tabi ona abayọ adayeba.",
        "Cassava Brown Streak Disease: Use virus-free cuttings.": "Arun ila pupa lori ege: Lo ege ti ko ni kokoro.",
        "Healthy cassava plant!": "Eweko ege ti o ni ilera!",
        "Upload Crop Image": "Po Aworan Ogbin",
        "Take a picture": "Ya aworan",
        "Detect Disease": "Ṣayẹwo Arun",
        "No disease detected.": "Ko si arun ti a rii.",
        "Detected Diseases and Solutions": "Awon Arun ati Itọju ti a Rii",
        "👉 Solution: ": "👉 Itọju: ",
        "What are the symptoms of this disease?": "Kini awon ami arun yii?",
        "How can I prevent it from spreading?": "Bawo ni mo se le da a duro lati tan kaakiri?",
        "Which pesticide or solution should I use?": "Kini oogun ti mo le lo?",
    },
    "Hausa": {
        "Cassava Bacterial Blight: Use resistant varieties.": "Cutar Bacterial a Manihot: Yi amfani da nau'in da ke da kariya.",
        "Cassava Mosaic Disease: Remove infected plants.": "Cutar Mosaic a Manihot: Cire shuke-shuken da suka kamu.",
        "Cassava Green Mite: Apply miticides or use biocontrol.": "Kwari a Manihot: Yi amfani da maganin kwari ko sarrafa halitta.",
        "Cassava Brown Streak Disease: Use virus-free cuttings.": "Cutar Brown Streak: Yi amfani da yanka marar cuta.",
        "Healthy cassava plant!": "Manihot lafiya!",
        "Upload Crop Image": "Dora Hoto na Shuka",
        "Take a picture": "Dauki hoto",
        "Detect Disease": "Gano Cuta",
        "No disease detected.": "Ba a gano wata cuta ba.",
        "Detected Diseases and Solutions": "Cututtuka da Magani da aka Gano",
        "👉 Solution: ": "👉 Magani: ",
        "What are the symptoms of this disease?": "Menene alamomin wannan cutar?",
        "How can I prevent it from spreading?": "Ta yaya zan hana ta yaduwa?",
        "Which pesticide or solution should I use?": "Wane maganin kwari zan yi amfani da shi?",
    },
    "Igbo": {
        "Cassava Bacterial Blight: Use resistant varieties.": "Ndị ọrịa nje bacteria na akpụ: Jiri ụdị dị ike.",
        "Cassava Mosaic Disease: Remove infected plants.": "Ọrịa mosaic na akpụ: Wepụ osisi ọrịa.",
        "Cassava Green Mite: Apply miticides or use biocontrol.": "Mite na akpụ: Tinye ọgwụ ma ọ bụ jiri usoro ntinye eke.",
        "Cassava Brown Streak Disease: Use virus-free cuttings.": "Ọrịa ntụpọ aja aja: Jiri akụkụ na-enweghị nje virus.",
        "Healthy cassava plant!": "Osisi akpụ dị mma!",
        "Upload Crop Image": "Bulite Foto nke Ọhịa",
        "Take a picture": "Were foto",
        "Detect Disease": "Chọpụta Ọrịa",
        "No disease detected.": "Enweghị ọrịa a chọpụtara.",
        "Detected Diseases and Solutions": "Ọrịa Chọpụtara na Ngwọta",
        "👉 Solution: ": "👉 Ngwọta: ",
        "What are the symptoms of this disease?": "Kedu ihe mgbaàmà ọrịa a?",
        "How can I prevent it from spreading?": "Kedu ka m ga-esi gbochie mgbasa ya?",
        "Which pesticide or solution should I use?": "Kedu ọgwụ m ga-eji mee ihe?",
    }
}

# =================== CONFIGURATION =======================
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

# ==================== UTILS =======================
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

def translate(text, lang):
    return translations.get(lang, {}).get(text, text)

# ====================== UI =======================
st.title("🌾 AI-Powered Crop Disease Detector")

st.session_state.selected_crop = st.selectbox("Select Crop", list(model_configs.keys()))
st.session_state.selected_lang = st.selectbox("Select Language", language_options)

uploaded_file = st.file_uploader(translate("Upload Crop Image", st.session_state.selected_lang), type=["jpg", "jpeg", "png"])
camera_file = st.camera_input(translate("Take a picture", st.session_state.selected_lang))

input_image = None
if uploaded_file:
    input_image = Image.open(uploaded_file).convert("RGB")
elif camera_file:
    input_image = Image.open(camera_file).convert("RGB")

if input_image:
    st.image(input_image, caption="Selected Image", use_column_width=True)

    if st.button(translate("Detect Disease", st.session_state.selected_lang)):
        config = model_configs[st.session_state.selected_crop]
        result = detect_image(input_image, config["model_id"], config["api_key"])

        if "predictions" in result and result["predictions"]:
            st.session_state.predictions = result["predictions"]
        else:
            st.session_state.predictions = []

# ================== RESULT DISPLAY =====================
if st.session_state.predictions is not None:
    if len(st.session_state.predictions) == 0:
        st.warning(translate("No disease detected.", st.session_state.selected_lang))
    else:
        config = model_configs[st.session_state.selected_crop]
        shown_classes = set()
        st.subheader(translate("Detected Diseases and Solutions", st.session_state.selected_lang))
        for pred in st.session_state.predictions:
            disease = pred["class"]
            if disease not in shown_classes:
                shown_classes.add(disease)
                solution = config["solutions"].get(disease, "No solution available.")
                st.markdown(f"**{translate(disease, st.session_state.selected_lang)}**")
                st.write(translate("👉 Solution: ", st.session_state.selected_lang) + translate(solution, st.session_state.selected_lang))

        # --------------- Chatbot Q&A -----------------
        st.subheader("💬 Questions and Answers")
        question = st.selectbox("Ask a question", [
            "What are the symptoms of this disease?",
            "How can I prevent it from spreading?",
            "Which pesticide or solution should I use?"
        ])
        answers = {
            "What are the symptoms of this disease?": "Symptoms include leaf discoloration, blight, or stunted growth.",
            "How can I prevent it from spreading?": "Isolate infected plants, practice crop rotation, and maintain field hygiene.",
            "Which pesticide or solution should I use?": "Use the recommended pesticides for each disease as listed above."
        }
        st.info(translate(answers[question], st.session_state.selected_lang))
