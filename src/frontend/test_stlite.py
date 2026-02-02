# Copyright (c) 2026 Brothertown Language
import streamlit as st

st.set_page_config(page_title="Stlite Test", page_icon="🧪")

st.title("Stlite Compatibility Test")
st.write("If you can see this, Stlite is working correctly!")

st.sidebar.header("Sidebar Test")
st.sidebar.write("Sidebar content is visible.")

name = st.text_input("What is your name?", "Tester")
if st.button("Greet"):
    st.balloons()
    st.success(f"Hello, {name}!")

st.info("System Check:")
st.write(f"Streamlit Version: {st.__version__}")
