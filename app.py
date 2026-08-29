"""A very simple calculator built with Streamlit."""

import streamlit as st

st.title("Simple Calculator")

a = st.number_input("First number", value=0.0)
b = st.number_input("Second number", value=0.0)
op = st.selectbox("Operation", ["+", "-", "*", "/", "^"])

if st.button("Calculate"):
    result = None
    error = None

    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    elif op == "^":
        if a == 0 and b < 0:
            error = "Cannot raise zero to a negative power."
        elif a < 0 and b != int(b):
            error = "Cannot raise a negative number to a fractional power."
        else:
            try:
                result = a ** b
            except OverflowError:
                error = "Result is too large to display."
    elif op == "/":
        if b == 0:
            error = "Cannot divide by zero."
        else:
            result = a / b
    else:
        error = f"Unsupported operation: {op}"

    if error is not None:
        st.error(error)
    else:
        st.success(f"{a} {op} {b} = {result}")
