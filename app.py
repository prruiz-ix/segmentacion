import streamlit as st

st.title("🧮 Mini Calculadora")
st.write("Elegí dos números y mirá la suma, fiera:")

# Entradas numéricas
x = st.number_input("Valor de X:", value=0)
y = st.number_input("Valor de Y:", value=0)

# Botón para calcular
if st.button("Calcular suma"):
    resultado = x + y
    st.success(f"La suma de {x} + {y} es: {resultado}")

