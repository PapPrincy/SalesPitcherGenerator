import streamlit as st
import requests

st.title("Sales Pitch and Email Content Generator")

# Get user input
url = st.text_input("Enter company URL:")

if st.button("Generate"):
 if url:
  try:
    response = requests.post("http://localhost:8000/generate_sales_pitch_and_email", data={"url": url})
    if response.status_code == 200:
       html_content = response.content.decode("utf-8")
       st.markdown(html_content, unsafe_allow_html=True)
    else:
       st.error(f"Error: {response.status_code} - {response.content.decode('utf-8')}")
  except requests.exceptions.RequestException as e:
    st.error(f"Request failed: {e}")
 else:
    st.error("Please enter a valid URL")