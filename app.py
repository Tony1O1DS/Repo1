import streamlit as st
import easyocr
from PIL import Image
import cv2
import numpy as np
import pandas as pd
import re

# Initialize OCR reader once
reader = easyocr.Reader(['en'])

st.set_page_config(page_title="Wedding Guest List OCR App", layout="wide")
st.title("📇 Wedding Guest List OCR App")
st.write("Upload images of visiting cards to automatically extract and edit guest details.")

uploaded_files = st.file_uploader(
    "Upload visiting card images (JPG/PNG)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

def preprocess_image(image):
    """Convert to grayscale, threshold, and denoise to improve OCR"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    denoised = cv2.medianBlur(thresh, 3)
    return denoised

def parse_fields(text):
    """Extract name, email, and Indian phone number from OCR text"""
    lines = text.strip().split('\n')
    name = lines[0] if lines else ""
    email = ""
    phone = ""

    # Find emails
    emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)
    if emails:
        email = emails[0]

    # Improved regex for Indian numbers
    # Optional +91 or 0, then number starting with 6-9, then 9 more digits
    phones = re.findall(r'(\+91[\-\s]?|0)?([6-9]\d{2}[\-\s]?\d{3}[\-\s]?\d{4})', text)
    if phones:
        raw = ''.join(phones[0])  # merge groups
        phone_clean = re.sub(r'[-\s]', '', raw)  # remove dashes/spaces
        # Standardize
        if phone_clean.startswith('+91'):
            phone = phone_clean
        elif phone_clean.startswith('0'):
            phone = '+91' + phone_clean[1:]
        elif len(phone_clean) == 10:
            phone = '+91' + phone_clean

    return name, email, phone

guest_data = []

if uploaded_files:
    st.info("Processing uploaded images...")
    for uploaded_file in uploaded_files:
        pil_image = Image.open(uploaded_file).convert("RGB")
        open_cv_image = np.array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()  # RGB to BGR

        processed_image = preprocess_image(open_cv_image)
        processed_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2RGB)

        # OCR
        results = reader.readtext(processed_image_rgb, detail=0)
        text = "\n".join(results)

        # Parse fields
        name, email, phone = parse_fields(text)

        guest_data.append({
            "Filename": uploaded_file.name,
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Raw_Text": text
        })

if guest_data:
    st.subheader("✏️ Edit Extracted Guest Details")

    df = pd.DataFrame(guest_data)

    # Editable table (including Name, Email, Phone)
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True
    )

    st.subheader("📥 Download Final Guest List")
    csv = edited_df.drop(columns=["Raw_Text"]).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name='guest_list.csv',
        mime='text/csv'
    )

    st.subheader("🔍 Full Raw OCR Text (for reference)")
    for idx, row in edited_df.iterrows():
        with st.expander(f"📝 {row['Filename']}"):
            st.text(row['Raw_Text'])