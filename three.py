import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_audio_recorder import st_audio_recorder
from scipy.io.wavfile import write
import tempfile
from openai import OpenAI

st.set_page_config(page_title="SMARTMIND Industrial Products", page_icon="🛠️", layout="wide")

ENQUIRIES_FILE = "enquiries.csv"

# --- Hardcoded Admin Credentials ---
ADMIN_CREDENTIALS = {
    "company": "1",
    "user": "2",
    "mobile": "3",
    "email": "4"
}

PRODUCTS = {
    "Camozzi": {
        "Cylinders": [
            "Series 60 ISO Cylinders",
            "Series 24 Compact Cylinders",
            "Series 32 Rodless Cylinders"
        ],
        "Valves": [
            "Series 3 Solenoid Valves",
            "Series 4 Mechanical Valves",
            "Series 6 Pneumatic Valves"
        ],
        "FRL Units": [
            "Series MX Filters",
            "Series MC Regulators",
            "Series MD Lubricators"
        ],
    },
    "SMC": {
        "Cylinders": [
            "CJ2 Series ISO Cylinders",
            "CQ2 Series Mini Cylinders",
            "MGP Series Guided Cylinders"
        ],
        "Valves": [
            "SY3000 Series Solenoid Valves",
            "VQZ100 Series Proportional Valves"
        ],
        "FRL Units": [
            "IDF Series Filters",
            "AR Series Regulators",
            "AL Series Lubricators",
            "AC Series Combinations"
        ],
    },
    "Metal Work": {
        "Cylinders": [
            "TP Series Round Cylinders",
            "ISO 15552 Series Compact Cylinders"
        ],
        "Valves": [
            "VY Series Mechanical Valves",
            "SOV Series Manual Valves",
            "VME Series Solenoid Valves"
        ],
        "FRL Units": [
            "Syntesi Filters",
            "New Deal Regulators",
            "New Deal Lubricators"
        ],
    },
    "UFlow": {
        "Valves": [
            "3X2 Double Solenoid Valves",
            "NAMUR Pulse Valves"
        ],
        "Cylinders": [
            "CN4 Series Hydraulic Cylinders",
            "PS7 Series Pneumatic Cylinders"
        ],
    }
}

# --- Initialize OpenAI Client ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- Helper Function: Record and Transcribe ---
def record_and_transcribe():
    DURATION = 10  # seconds of recording
    SAMPLE_RATE = 16000

    st.info("🎙️ Recording... Please speak now!")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    st.success("✅ Recording finished!")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        write(tmpfile.name, SAMPLE_RATE, recording)
        audio_path = tmpfile.name

    # --- Transcribe ---
    with open(audio_path, "rb") as audio_file:
        translation = client.audio.translations.create(
            model="whisper-1",
            file=audio_file
        )

    raw_text = translation.text

    # --- Refine with GPT ---
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. The text given to you is the translated (english) version of the comments given by a user on purchase of pneumatic products from Smartmind Industrial Products, a trading company. Refine translated text for clarity and fix mistakes."},
            {"role": "user", "content": raw_text}
        ]
    )

    refined_text = response.choices[0].message.content
    return refined_text

# --- LOGIN PAGE ---
def login_page():
    st.title("🛠️ SMARTMIND Industrial Products")
    st.markdown("### 🔐 Login")

    company_name = st.text_input("🏢 Company Name")
    user_name = st.text_input("👤 Your Name")
    mobile = st.text_input("📞 Mobile Number")
    email = st.text_input("✉️ Email ID")

    if st.button("Login"):
        if (
            company_name.strip() == ADMIN_CREDENTIALS["company"]
            and user_name.strip() == ADMIN_CREDENTIALS["user"]
            and mobile.strip() == ADMIN_CREDENTIALS["mobile"]
            and email.strip() == ADMIN_CREDENTIALS["email"]
        ):
            st.session_state.role = "admin"
            st.session_state.page = "admin"
            st.success("✅ Logged in as Admin")
            st.rerun()
        elif company_name and user_name and mobile and email:
            st.session_state.role = "user"
            st.session_state.company = company_name
            st.session_state.user = user_name
            st.session_state.mobile = mobile
            st.session_state.email = email
            st.session_state.page = "enquiry"
            st.success(f"✅ Welcome {user_name}, you are logged in!")
            st.rerun()
        else:
            st.error("⚠️ Please fill all details to log in")


# --- ENQUIRY FORM (USER) ---
def enquiry_page():
    st.header("📋 Pneumatic Product Enquiry Form")

    if "products" not in st.session_state:
        st.session_state.products = []

    st.subheader("Product Details")
    brand = st.radio(
        "Product Make/Brand",
        ["Camozzi", "SMC", "UFlow", "Metal Work"],
        horizontal=True
    )

    # Dropdown for Product Type
    product_types = ["Please select any one option"] + list(PRODUCTS[brand].keys())
    component_type = st.selectbox("🔧 Type of Pneumatic Component", product_types)

    # Dropdown for Grade (depends on component type)
    grades = ["Please select any one option"]
    if component_type != "Please select any one option":
        grades = ["Please select any one option"] + PRODUCTS[brand][component_type]
    grade = st.selectbox("⚙️ Grade of Pneumatic Component", grades)

    quantity = st.number_input("🔢 Quantity", min_value=1, step=1)

    # --- Comments with Voice Input ---
    comments = st.text_area("📝 Additional Comments", placeholder="Enter any extra requirements")

    if st.button("🎤 Record Voice Comment"):
        refined_text = record_and_transcribe()
        comments += "\n" + refined_text  # append refined voice input
        st.session_state.comments = comments
        st.success("✅ Voice note added!")

    if "comments" in st.session_state:
        comments = st.session_state.comments

    if st.button("➕ Add Product"):
        if component_type == "Please select any one option" or grade == "Please select any one option":
            st.error("⚠️ Please select both Product Type and Grade")
        else:
            product = {
                "Brand": brand,
                "Component Type": component_type,
                "Grade": grade,
                "Quantity": quantity,
                "Comments": comments
            }
            st.session_state.products.append(product)
            st.success("✅ Product added successfully!")

    # Display table if products exist
    if st.session_state.products:
        st.subheader("📋 Products Added")

        df = pd.DataFrame(st.session_state.products)
        df.index = range(1, len(df) + 1)
        df.index.name = "S.No."

        st.dataframe(df, use_container_width=True)

        delete_choice = st.selectbox(
            "🗑️ Select product to delete",
            options=["None"] + [f"S.No.{i}" for i in df.index],
            key="delete_choice"
        )

        if delete_choice != "None":
            if st.button("Confirm Delete"):
                to_delete = int(delete_choice.replace("S.No.", ""))
                st.session_state.products.pop(to_delete - 1)
                st.success(f"✅ Deleted entry {delete_choice}")
                st.rerun()

    if st.button("📨 Submit Enquiry"):
        if st.session_state.products:
            enquiry = {
                "Company": st.session_state.company,
                "User": st.session_state.user,
                "Mobile": st.session_state.mobile,
                "Email": st.session_state.email,
                "Products": str(st.session_state.products),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            df = pd.DataFrame([enquiry])
            try:
                old = pd.read_csv(ENQUIRIES_FILE)
                df = pd.concat([old, df], ignore_index=True)
            except FileNotFoundError:
                pass
            df.to_csv(ENQUIRIES_FILE, index=False)

            st.success("🎉 Enquiry submitted successfully!")
            st.session_state.products = []  # Reset products
            st.session_state.comments = ""  # Reset comments
        else:
            st.error("⚠️ Please add at least one product before submitting.")

    if st.button("🚪 Log Out"):
        st.session_state.clear()
        st.session_state.page = "login"
        st.rerun()


# --- ADMIN DASHBOARD ---
def admin_page():
    st.header("📊 Admin Dashboard")
    try:
        data = pd.read_csv(ENQUIRIES_FILE)
        st.dataframe(data)
    except FileNotFoundError:
        st.warning("No enquiries submitted yet.")

    if st.button("🚪 Log Out"):
        st.session_state.clear()
        st.session_state.page = "login"
        st.rerun()


# --- ROUTER ---
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "enquiry":
    enquiry_page()
elif st.session_state.page == "admin":
    admin_page()

