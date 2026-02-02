# Copyright (c) 2026 Brothertown Language
import streamlit as st
import httpx
import json

st.set_page_config(page_title="SNEA Dev Info", page_icon="🛠️")

st.title("SNEA Editor - System Info")
st.write("This is a basic Stlite app to verify connectivity with the backend.")

if st.button("Fetch Backend Info"):
    with st.spinner("Calling /api/health..."):
        try:
            # Using relative path for unified architecture
            response = httpx.get("/api/health", timeout=5.0)
            if response.status_code == 200:
                st.success("Backend is reachable!")
                st.json(response.json())
            else:
                st.error(f"Backend returned error: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

st.divider()
st.info("Environment Check")
st.write(f"Streamlit version: {st.__version__}")
