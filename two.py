import streamlit as st
import pandas as pd
from datetime import datetime

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

# --- Initialize session state ---
if "page" not in st.session_state:
    st.session_state.page = "login"


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
    comments = st.text_area("📝 Additional Comments", placeholder="Enter any extra requirements")

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

        # Convert products to DataFrame with S.No.
        df = pd.DataFrame(st.session_state.products)
        df.index = range(1, len(df) + 1)
        df.index.name = "S.No."

        # Display formatted table
        st.dataframe(
            df.style.set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'center')]},
                {'selector': 'td', 'props': [('text-align', 'center')]}]
            ),
            use_container_width=True
        )

        # Dropdown to delete a row
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
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "enquiry":
    enquiry_page()
elif st.session_state.page == "admin":
    admin_page()
