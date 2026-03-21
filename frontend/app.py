import streamlit as st
import requests
import os

st.title("Vel-Kural: Thirukkural Moral Story Generator")

# We default to looking for a backend service in Docker, or localhost if running natively
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.markdown("Select a Thirukkural to generate a 1000-word narrative moral story in both English and Tamil!")

kural_number = st.number_input("Enter Kural Number (1-1330)", min_value=1, max_value=1330, value=1)

if st.button("Generate Moral Story"):
    with st.spinner("Agent is generating 1000-word stories in English and Tamil (This may take a minute)..."):
        try:
            response = requests.post(f"{BACKEND_URL}/generate_story", json={"kural_number": kural_number})
            if response.status_code == 200:
                data = response.json()
                
                tab1, tab2 = st.tabs(["English Story", "தமிழ் கதை (Tamil Story)"])
                
                with tab1:
                    st.write(data.get("english_story", ""))
                    
                with tab2:
                    st.write(data.get("tamil_story", ""))
            else:
                st.error("Failed to generate story from the agent. Please check backend logs.")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}. Ensure backend is running.")
