import streamlit as st
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards

st.set_page_config(page_title="Калькулятор НМЦК", layout="centered")

# --- Инициализация состояний ---
if 'prices' not in st.session_state:
    st.session_state.prices = []
if 'price_input' not in st.session_state:
    st.session_state.price_input = ""

# --- Функция расчета НМЦК ---
def calculate_nmck(prices):
    n = len(prices)
    if n == 0:
        return None, None, None, "Введите хотя бы одну цену"

    mean_price = np.mean(prices)
    std_dev = np.std(prices, ddof=1)
    variation_coeff = (std_dev / mean_price) * 100 if mean_price != 0 else None

    return mean_price, std_dev, variation_coeff, None

# --- Функция добавления цены ---
def add_price():
    try:
        price = float(st.session_state.price_input.replace(",", "."))
        if price >= 0.01:
            st.session_state.prices.append(price)
            st.session_state.price_input = ""
        else:
            st.warning("Цена должна быть не меньше 0.01")
    except ValueError:
        st.error("Введите корректное число")

def custom_metric(label, value, unit=""):
    st.markdown(f"""
        <div style="background-color:#e0e0e0;padding:16px;border-radius:10px;margin-bottom:10px;">
            <div style="font-size:16px;color:#333;font-weight:600;">{label}</div>
            <div style="font-size:24px;color:#000;font-weight:700;">{value} {unit}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Стили CSS ---
st.markdown("""
    <style>
    .css-18e3th9 {
        background-color: #0b2545 !important;
        color: #ffffff !important;
    }
    .css-1d391kg {
        background-color: transparent !important;
    }
    div[data-testid="metric-container"] {
        background-color: #e0e0e0 !important;
        color: #111111 !important;
        border-radius: 8px;
        padding: 12px;
    }
    div[data-testid="metric-value"] {
        color: #111111 !important;
        font-weight: 700;
        opacity: 1 !important;
    }
    div[data-testid="metric-label"] {
        color: #333333 !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] svg {
        fill: #111111 !important;
    }
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 8px !important;
        height: 3em !important;
        width: 100% !important;
    }
    .stTextInput>div>input {
        border-radius: 8px !important;
        color: #111111 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Заголовки ---
st.title("📊 Калькулятор НМЦК")
st.caption("Введите цены от поставщиков и получите расчёты средней цены и коэффициента вариации")

# --- Ввод цены ---
st.text_input("Введите цену поставщика", key="price_input")

# --- Кнопки ---
col1, col2 = st.columns([1, 1])
with col1:
    st.button("➕ Добавить цену", on_click=add_price)

with col2:
    if st.button("🗑 Очистить список"):
        st.session_state.clear()
        st.rerun()  # ✅ перезагрузка страницы без ошибок

# --- Показ введённых цен ---
if st.session_state.get("prices"):  # безопасный доступ
    st.subheader("📌 Введенные цены:")
    st.write(", ".join(f"{p:.2f}" for p in st.session_state.prices))

# --- Расчет и вывод результатов ---
if st.session_state.get("prices"):
    mean_price, std_dev, variation_coeff, _ = calculate_nmck(st.session_state.prices)
    st.divider()
    st.subheader("📈 Результаты расчета")
    col1, col2, col3 = st.columns(3)
    with col1:
        custom_metric("Средняя цена", f"{mean_price:,.2f}", "₽")
    with col2:
        custom_metric("СКО", f"{std_dev:,.2f}")
    with col3:
        custom_metric("Коэф. вариации", f"{variation_coeff:,.2f}", "%")

    if variation_coeff > 33:
        st.warning("Коэффициент вариации превышает 33% — проверьте данные на выбросы.")
else:
    st.info("Добавьте цены, чтобы рассчитать НМЦК.")
