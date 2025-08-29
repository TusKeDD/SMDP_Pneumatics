import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="SMARTMIND INDUSTRIAL PRODUCTS",
    page_icon="🛠️",
    layout="wide"
)

# --- App Title ---
st.title("🛠️ SMARTMIND INDUSTRIAL PRODUCTS")
st.markdown("### Pneumatic Product Enquiry Form")

# Initialize session state for products
if "products" not in st.session_state:
    st.session_state.products = []

# --- User Details ---
st.header("📋 Company & User Details")
company_name = st.text_input("🏢 Company Name")
user_name = st.text_input("👤 Your Name")
contact = st.text_input("📞 Contact Details (Phone / Email)")

# --- Product Entry Form ---
st.header("📦 Product Details")

brand = st.radio(
    "Product Make/Brand",
    ["Camozzi", "SMC", "UFlow", "Metal Work"],
    horizontal=True
)

component_type = st.text_input("🔧 Type of Pneumatic Component (e.g., Cylinder, Valve)")
grade = st.text_input("⚙️ Grade of Pneumatic Component (if any)")
quantity = st.number_input("🔢 Quantity", min_value=1, step=1)
comments = st.text_area("📝 Additional Comments", placeholder="Enter any extra requirements")

# Add product button
if st.button("➕ Add Product"):
    product = {
        "Brand": brand,
        "Component Type": component_type,
        "Grade": grade,
        "Quantity": quantity,
        "Comments": comments
    }
    st.session_state.products.append(product)
    st.success("✅ Product added successfully!")

# Show added products
if st.session_state.products:
    st.subheader("🛍️ Products Added")
    st.table(pd.DataFrame(st.session_state.products))

# Submit final enquiry
if st.button("📨 Submit Enquiry"):
    if company_name and user_name and contact and st.session_state.products:
        enquiry = {
            "Company": company_name,
            "User": user_name,
            "Contact": contact,
            "Products": st.session_state.products,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to CSV (you can replace with DB later)
        df = pd.DataFrame([enquiry])
        try:
            old = pd.read_csv("enquiries.csv")
            df = pd.concat([old, df], ignore_index=True)
        except FileNotFoundError:
            pass
        df.to_csv("enquiries.csv", index=False)

        st.success("🎉 Enquiry submitted successfully!")
        st.session_state.products = []  # Reset products
    else:
        st.error("⚠️ Please fill all details and add at least one product before submitting.")

# --- Admin Section ---
st.markdown("---")
st.header("🔑 Admin Section")
admin_pass = st.text_input("Enter Admin Password", type="password")

if admin_pass == "smartmind123":  # change this password for production
    st.success("✅ Access Granted")
    try:
        data = pd.read_csv("enquiries.csv")
        st.dataframe(data)
    except FileNotFoundError:
        st.warning("No enquiries submitted yet.")
