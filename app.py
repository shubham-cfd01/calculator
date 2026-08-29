"""A very simple calculator built with Streamlit."""

import streamlit as st

st.title("Simple Calculator")

a = st.number_input("First number", value=0.0)
b = st.number_input("Second number", value=0.0)
op = st.selectbox("Operation", ["+", "-", "*", "/"])

if st.button("Calculate"):
    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    elif b == 0:
        result = None
    else:
        result = a / b

    if result is None:
        st.error("Cannot divide by zero.")
    else:
        st.success(f"{a} {op} {b} = {result}")
