import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
from googletrans import Translator

# Translator
translator = Translator()

# Supported languages and codes
languages = {
    "English": "en",
    "Yoruba": "yo",
    "Hausa": "ha",
    "Igbo": "ig",
    "French": "fr",
    "Swahili": "sw"
}

# Roboflow configs
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

# Inbuilt chatbot Q&A
chatbot_questions = {
    "en": {
        "How do I prevent diseases?": "Ensure good farm hygiene, use certified seeds, and rotate crops.",
        "Can I use organic methods?": "Yes, biopesticides and neem extracts are effective for some conditions.",
        "What should I do after detection?": "Isolate the infected plants and apply recommended treatments."
    },
    "yo": {
        "Báwo ni mo ṣe le dena àrùn?": "Lo irugbin tó dáa, pa oko mọ́, àti yí oko padà lẹ́ẹ̀kan sí lẹ́ẹ̀kan.",
        "Ṣé mo le lo àbínibí tàbí ogbin aláyọ?": "Bẹ́ẹ̀ni, àwọn ọgbìn bii neem le ran lọwọ.",
        "Kí ni kí n ṣe lẹ́yìn àyẹ̀wò?": "Yà àwọn èso tó ní àrùn kúrò, kí o sì lo ìtọ́jú tó yẹ."
    },
    "ha": {
        "Ta yaya zan hana cuta?": "Yi amfani da iri masu kyau, tsaftace gona, da jujjuya amfanin gona.",
        "Zan iya amfani da hanyoyin gargajiya?": "I, za ka iya amfani da magungunan gargajiya kamar neem.",
        "Me zan yi bayan gano cutar?": "Killace shuka mai cuta kuma kayi amfani da magani da ya dace."
    },
    "ig": {
        "Kedu ka m ga-esi gbochie ọrịa?": "Jiri mkpụrụ dị ọcha, mee ka ubi dị ọcha, na-agbanwe ogige ugbo.",
        "Enwere m ike iji usoro organic?": "Ee, ọgwụ sitere n’ime osisi dị ka neem bara uru.",
        "Gịnị ka m ga-eme mgbe a chọpụtara ọrịa?": "Kewapụ osisi nwere ọrịa ma jiri ọgwụ kwesịrị ekwesị."
    },
    "fr": {
        "Comment prévenir les maladies ?": "Utilisez des semences certifiées, pratiquez l’hygiène et la rotation des cultures.",
        "Puis-je utiliser des méthodes biologiques ?": "Oui, les biopesticides comme le neem sont utiles.",
        "Que faire après détection ?": "Isolez les plantes malades et appliquez un traitement adapté."
    },
    "sw": {
        "Ninawezaje kuzuia magonjwa?": "Tumia mbegu bora, fanya usafi wa shamba, na fanya mzunguko wa mazao.",
        "Je, naweza kutumia njia za asili?": "Ndiyo, dawa za mimea kama neem husaidia.",
        "Nifanye nini baada ya kugundua ugonjwa?": "Tenganisha mimea iliyougua na tumia tiba inayofaa."
    }
}

# Translate text
def translate_text(text, lang_code):
    if lang_code == "en":
        return text
    try:
        translated = translator.translate(text, dest=lang_code).text
        return translated
    except:
        return text  # fallback

# Convert image to base64
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# Detect using Roboflow
def detect_image(image, model_id, api_key):
    base64_img = image_to_base64(image)
    url = f"https://detect.roboflow.com/{model_id}?api_key={api_key}&confidence=35"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=base64_img, headers=headers)
    return response.json()

# Streamlit UI
st.set_page_config(page_title="🌱 Smart Crop Doctor", layout="centered")
st.title("🌾 Smart Crop Disease Detector")

# Sidebar
crop = st.sidebar.selectbox("Select Crop", list(model_configs.keys()))
language = st.sidebar.selectbox("Select Language", list(languages.keys()))
lang_code = languages[language]

uploaded_file = st.file_uploader("Upload Image of Crop Leaf", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("Or Take a Picture")

input_image = None
if uploaded_file:
    input_image = Image.open(uploaded_file).convert("RGB")
elif camera_file:
    input_image = Image.open(camera_file).convert("RGB")

if input_image:
    st.image(input_image, caption=translate_text("Uploaded Image", lang_code), use_container_width=True)

    detect_clicked = st.button("Detect Disease")
    if detect_clicked:
        with st.spinner(translate_text("Analyzing Image...", lang_code)):
            config = model_configs[crop]
            result = detect_image(input_image, config["model_id"], config["api_key"])
            predictions = result.get("predictions", [])
            shown_classes = set()

            if predictions:
                for pred in predictions:
                    disease = pred["class"]
                    if disease not in config["solutions"]:
                        continue

                    if disease not in shown_classes:
                        shown_classes.add(disease)
                        solution = config["solutions"].get(disease, "No solution available.")
                        st.subheader(f"🧬 {translate_text(disease, lang_code)}")
                        st.success(f"✅ {translate_text(solution, lang_code)}")

                if not shown_classes:
                    st.warning(translate_text("⚠️ No plant-related disease detected. Try a clearer crop image.", lang_code))
            else:
                st.error(translate_text("❌ No plant detected. Please snap or upload a crop image.", lang_code))

    # 👇 This is now OUTSIDE the button logic, so it's always visible
    st.markdown("---")
    st.subheader("🧠 " + translate_text("Ask a Question", lang_code))

    question_options = list(chatbot_questions[lang_code].keys())
    selected_question = st.selectbox(translate_text("Select a question:", lang_code), question_options)

    if selected_question:
        st.info(chatbot_questions[lang_code][selected_question])
