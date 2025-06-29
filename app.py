import streamlit as st
import easyocr
import pandas as pd
from PIL import Image
import numpy as np

# Optional: Initialize or load your guest list DataFrame
if "guest_list" not in st.session_state:
    st.session_state["guest_list"] = pd.DataFrame(columns=["Name", "Phone", "Email", "Address", "Text"])

st.title("📇 Indian Visiting Card OCR App")

uploaded_file = st.file_uploader("Upload a visiting card image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded card', use_column_width=True)

    reader = easyocr.Reader(['en'])  # Add 'hi' if your cards have Hindi
    with st.spinner("Reading text..."):
        result = reader.readtext(np.array(image))

    # Combine all recognized text into a single string
    extracted_text = "\n".join([res[1] for res in result])

    st.subheader("Extracted text:")
    st.text_area("", extracted_text, height=200)

    st.subheader("Edit details before saving:")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    address = st.text_area("Address")

    if st.button("Save guest"):
        # Add new guest to the DataFrame
        new_guest = {
            "Name": name,
            "Phone": phone,
            "Email": email,
            "Address": address,
            "Text": extracted_text
        }
        st.session_state["guest_list"] = pd.concat([
            st.session_state["guest_list"],
            pd.DataFrame([new_guest])
        ], ignore_index=True)
        st.success(f"✅ Guest saved: {new_guest}")

# Optional: Show the guest list table
if not st.session_state["guest_list"].empty:
    st.subheader("📋 Guest List")
    st.dataframe(st.session_state["guest_list"])
