import streamlit as st
import numpy as np
from statsmodels.stats.proportion import proportions_ztest, proportion_effectsize
from statsmodels.stats.power import NormalIndPower

# ---------------------------------------------
# FUNCIONES
# ---------------------------------------------

def calcular_tamano_muestra(p_control, mde=None, p_tratamiento=None,
                            alpha=0.1, power=0.6, ratio=1, alternative='two-sided'):
    if mde is not None:
        p_tratamiento = p_control + mde
    elif p_tratamiento is None:
        raise ValueError("Debes proporcionar 'p_tratamiento' o 'mde'.")

    effect_size = proportion_effectsize(p_tratamiento, p_control)
    power_analysis = NormalIndPower()
    n_trat = power_analysis.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        ratio=ratio,
        alternative=alternative
    )
    n_ctrl = n_trat * ratio
    return int(np.ceil(n_trat)), int(np.ceil(n_ctrl)), abs(p_tratamiento - p_control)

def prueba_significatividad(exitos_trat, n_trat, exitos_ctrl, n_ctrl,
                            alpha=0.1, alternative='two-sided'):
    counts = np.array([exitos_trat, exitos_ctrl])
    nobs = np.array([n_trat, n_ctrl])
    stat, p_value = proportions_ztest(counts, nobs, alternative=alternative)

    p_trat_obs = exitos_trat / n_trat
    p_ctrl_obs = exitos_ctrl / n_ctrl
    diff_obs = p_trat_obs - p_ctrl_obs

    return {
        "p_trat": p_trat_obs,
        "p_ctrl": p_ctrl_obs,
        "diff": diff_obs,
        "z": stat,
        "p_value": p_value,
        "significativo": p_value < alpha
    }

def calcular_potencia(exitos_trat, n_trat, exitos_ctrl, n_ctrl,
                      alpha=0.1, alternative='two-sided'):
    p_trat_obs = exitos_trat / n_trat
    p_ctrl_obs = exitos_ctrl / n_ctrl
    effect_size = proportion_effectsize(p_trat_obs, p_ctrl_obs)
    ratio = n_ctrl / n_trat
    power_analysis = NormalIndPower()
    potencia = power_analysis.power(effect_size=effect_size,
                                    nobs1=n_trat,
                                    alpha=alpha,
                                    ratio=ratio,
                                    alternative=alternative)
    return potencia

# ---------------------------------------------
# INTERFAZ STREAMLIT
# ---------------------------------------------
st.title("🧪 Calculadora de A/B Testing de Proporciones")
st.subheader("Modificá los parámetros para analizar tu experimento, fiera 💪")

st.markdown("""
Esta app te ayuda a:
1. **Definir el tamaño de muestra necesario** antes de lanzar un experimento.  
2. **Evaluar la significancia estadística** después del test.  
3. **Calcular la potencia post-hoc** (para saber si tu muestra fue suficiente).  
""")

st.divider()

# --- Inputs ---
st.header("1️⃣ Parámetros del experimento")

col1, col2 = st.columns(2)
with col1:
    p_control = st.number_input("Proporción del grupo control (p_control)", 0.0, 1.0, 0.25, step=0.01)
    mde = st.number_input("Diferencia mínima detectable (MDE)", -0.5, 0.5, -0.01, step=0.005)
    alpha = st.selectbox("Nivel de significancia (α)", [0.1, 0.05, 0.01], index=1)
with col2:
    power = st.slider("Potencia deseada (1 - β)", 0.5, 0.95, 0.8, 0.05)
    ratio = st.number_input("Ratio n_control / n_tratamiento", 0.1, 10.0, 1.0, 0.1)
    alternative = st.selectbox("Tipo de prueba", ['two-sided', 'larger', 'smaller'], index=0)

# --- Botón tamaño de muestra ---
if st.button("📏 Calcular tamaño de muestra"):
    n_trat, n_ctrl, mde_real = calcular_tamano_muestra(p_control, mde=mde, alpha=alpha, power=power, ratio=ratio, alternative=alternative)
    st.success(f"Necesitás **{n_trat:,}** observaciones en tratamiento y **{n_ctrl:,}** en control.")
    st.write(f"MDE absoluto: {mde_real:.4f}")

st.divider()

# --- Prueba de significancia ---
st.header("2️⃣ Evaluar resultado del experimento")

col3, col4 = st.columns(2)
with col3:
    exitos_trat = st.number_input("Éxitos en tratamiento", 0, 1_000_000, 1393)
    n_trat = st.number_input("Tamaño tratamiento", 1, 1_000_000, 5805)
with col4:
    exitos_ctrl = st.number_input("Éxitos en control", 0, 1_000_000, 6436)
    n_ctrl = st.number_input("Tamaño control", 1, 1_000_000, 24757)

if st.button("🔬 Prueba de significancia"):
    res = prueba_significatividad(exitos_trat, n_trat, exitos_ctrl, n_ctrl, alpha=alpha, alternative=alternative)
    st.metric("p-valor", f"{res['p_value']:.4f}")
    st.metric("Diferencia observada", f"{res['diff']:+.4f}")
    if res["significativo"]:
        st.success("✅ Diferencia significativa")
    else:
        st.warning("⚠️ No significativa")

st.divider()

# --- Potencia post-hoc ---
st.header("3️⃣ Calcular potencia post-hoc")
if st.button("⚡ Calcular potencia"):
    potencia = calcular_potencia(exitos_trat, n_trat, exitos_ctrl, n_ctrl, alpha=alpha, alternative=alternative)
    st.metric("Potencia observada", f"{potencia:.3f}")
    if potencia < 0.8:
        st.warning("Potencia baja → riesgo de falso negativo")
    else:
        st.success("Potencia suficiente 💪")

st.markdown("---")
st.caption("Hecho por Fiera para la patria 🇦🇷")
