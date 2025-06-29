import streamlit as st
import easyocr
import pandas as pd
from PIL import Image
import io
import re
import numpy as np


# Title
st.title("💌 Wedding Guest List OCR App (India)")

# File uploader
uploaded_file = st.file_uploader("Upload a visiting card image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Visiting Card', use_column_width=True)

    # OCR
    reader = easyocr.Reader(['en'])  # use English, works fine for most Indian cards
    result = reader.readtext(np.array(image), detail=0)
    full_text = "\n".join(result)

    # Extract potential details
    # Naive regex patterns for India (feel free to refine)
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", full_text)
    phones = re.findall(r"\+91[-\s]?\d{10}|\b\d{10}\b", full_text)

    # Prepare DataFrame with editable fields
    data = {
        "Name": [""],
        "Phone": [phones[0] if phones else ""],
        "Email": [emails[0] if emails else ""],
        "Address": [""],
        "Text": [full_text]
    }
    df = pd.DataFrame(data)

    st.subheader("✏️ Review & Edit Guest Details")
    edited_df = st.data_editor(df)

    # Show the final data
    if st.button("✅ Save Guest"):
        st.success("Guest details saved:")
        st.write(edited_df)