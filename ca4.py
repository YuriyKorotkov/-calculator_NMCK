import re
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Калькулятор стоимости", layout="centered")

# === Стили (замени этим блоком в твоём файле) ===
st.markdown("""
<style>
/* Общий фон и текст — пепельно-синий фон, весь текст белый */
body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainContent"] {
    background-color: #61676e !important; /* пепельно-синий с лёгкой холодной ноткой */
    color: #ffffff !important;
    font-family: 'Segoe UI', sans-serif;
}

/* Лёгкая тень для текста, чтобы белый был контрастнее */
body, h1, h2, h3, p, label, span, div, .stMarkdown {
    text-shadow: 0 1px 2px rgba(0,0,0,0.6);
}

/* Заголовок */
h1 {
    color: #ffffff !important;
    font-weight: 800;
    font-size: 2rem;
    text-align: center;
    margin-bottom: 0.5em;
}

/* Подзаголовок */
.subheader {
    color: #ffffff !important;
    font-weight: 700;
    font-size: 1.05rem;
    margin-top: 10px;
    margin-bottom: 6px;
    text-align: center;
}

/* Горизонтальные блоки кнопок — выравнивание */
div[data-testid="stHorizontalBlock"] {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 10px;
}

/* Стандартные кнопки — зелёные, текст белый */
div[data-testid="stHorizontalBlock"] button,
.stButton>button {
    margin: 3px 6px;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 0.6em 1.4em;
    transition: all 0.18s ease;
    background-color: #009639 !important; /* фирменный зелёный */
    color: #ffffff !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.25) !important;
}

/* Hover у кнопок */
div[data-testid="stHorizontalBlock"] button:hover,
.stButton>button:hover {
    transform: scale(1.03);
    background-color: #2fb14a !important;
}

/* Выделенная кнопка (selected) — масштаб и градиент */
.selected-btn {
    background: linear-gradient(135deg, #66bb6a, #009639) !important;
    color: #ffffff !important;
    transform: scale(1.08) !important;
    box-shadow: 0 6px 14px rgba(0,0,0,0.5) !important;
    border: 2px solid rgba(255,255,255,0.06) !important;
}

/* Блок цены */
.price-box {
    background: #1f6b2f !important; /* тёмно-зелёный фон блока цены */
    color: #ffffff !important;
    padding: 18px;
    border-radius: 12px;
    font-size: 1.3rem;
    font-weight: 700;
    text-align: center;
    border: 2px solid #007f2f !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
    margin-top: 12px;
}

/* Чекбоксы и подписи — белые */
.stCheckbox>div, label, p, span, .stMarkdown {
    color: #ffffff !important;
}

/* Принудительно белый текст в некоторых компонентах Streamlit */
[data-testid="stTextInput"] label, 
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# === Заголовок ===
st.markdown("<h1>Калькулятор стоимости<br>«Дом на Века»</h1>", unsafe_allow_html=True)

st.markdown("<div class='subheader'>Выберите параметры и допы</div>", unsafe_allow_html=True)

# === Загрузка данных ===
@st.cache_data
def load_data(file_path="Прайс ДНВ 2025 (13 проектов).xlsx"):
    df = pd.read_excel(file_path, header=None)
    df = df.dropna(how="all")
    return df

df = load_data()

# === Парсеры вспомогательные ===
def split_lines(cell):
    if cell is None or (isinstance(cell, float) and math.isnan(cell)):
        return []
    s = str(cell).replace("\r", "\n").replace("\xa0", " ")
    return [p.strip() for p in s.split("\n") if p.strip()]

def to_int_from_str(s):
    if s is None: return None
    if isinstance(s, (int, float)) and not math.isnan(s): return int(s)
    digits = re.sub(r'\D', '', str(s))
    return int(digits) if digits else None

def get_price_from_cells(cell, next_cell, payment):
    parts = split_lines(cell)
    if parts:
        if len(parts) >= 2:
            return to_int_from_str(parts[0]) if payment == "Наличные" else to_int_from_str(parts[-1])
        elif payment == "Наличные":
            return to_int_from_str(parts[0])
        else:
            next_parts = split_lines(next_cell)
            return to_int_from_str(next_parts[0]) if next_parts else None
    next_parts = split_lines(next_cell)
    if not next_parts: return None
    return to_int_from_str(next_parts[0]) if payment == "Наличные" else to_int_from_str(next_parts[-1])

# === Сбор данных из прайса ===
project_rows = df[df[0].astype(str).str.strip().str.startswith("«", na=False)]
projects = project_rows[0].tolist()
data = {}

for i, row in project_rows.iterrows():
    project_name = str(row[0]).strip()
    next_row = df.iloc[i + 1] if i + 1 < len(df) else None
    data[project_name] = {}
    for finish_type, col_start in zip(["Черновая", "Предчистовая"], [1, 3]):
        cell_sil = row[col_start] if col_start < len(row) else None
        cell_ker = row[col_start + 1] if (col_start + 1) < len(row) else None
        next_cell_sil = next_row[col_start] if (next_row is not None and col_start < len(next_row)) else None
        next_cell_ker = next_row[col_start + 1] if (next_row is not None and (col_start + 1) < len(next_row)) else None
        sil_cash = get_price_from_cells(cell_sil, next_cell_sil, "Наличные")
        sil_mort = get_price_from_cells(cell_sil, next_cell_sil, "Ипотека")
        ker_cash = get_price_from_cells(cell_ker, next_cell_ker, "Наличные")
        ker_mort = get_price_from_cells(cell_ker, next_cell_ker, "Ипотека")
        data[project_name][finish_type] = {
            "Силикатный": {"Наличные": sil_cash, "Ипотека": sil_mort},
            "Керамический": {"Наличные": ker_cash, "Ипотека": ker_mort}
        }

# === Инициализация состояния ===
if "finish_choice" not in st.session_state:
    st.session_state["finish_choice"] = None  # "Черновая" или "Предчистовая"
if "show_addons_plus" not in st.session_state:
    st.session_state["show_addons_plus"] = False
if "show_addons_minus" not in st.session_state:
    st.session_state["show_addons_minus"] = False

# === Кнопки выбора отделки + видимость допов (одинаково визуально) ===
def finish_buttons():
    cols = st.columns(4)
    # Черновая
    label_ch = "✅ Черновая" if st.session_state["finish_choice"] == "Черновая" else "Черновая"
    if cols[0].button(label_ch, key="btn_chern"):
        st.session_state["finish_choice"] = "Черновая"
        # при переключении прячем допы минус
        st.session_state["show_addons_minus"] = False

    # место для Допы + (появляется только при Черновая)
    if st.session_state["finish_choice"] == "Черновая":
        label_add_plus = "✅ Допы +" if st.session_state["show_addons_plus"] else "Допы +"
        if cols[1].button(label_add_plus, key="btn_add_plus"):
            st.session_state["show_addons_plus"] = not st.session_state["show_addons_plus"]
            # при включении плюсов выключаем минусы
            if st.session_state["show_addons_plus"]:
                st.session_state["show_addons_minus"] = False
    else:
        cols[1].write("")  # пустой слот

    # Предчистовая
    label_pr = "✅ Предчистовая" if st.session_state["finish_choice"] == "Предчистовая" else "Предчистовая"
    if cols[2].button(label_pr, key="btn_predch"):
        st.session_state["finish_choice"] = "Предчистовая"
        # при переключении прячем допы плюс
        st.session_state["show_addons_plus"] = False

    # место для Допы - (появляется только при Предчистовая)
    if st.session_state["finish_choice"] == "Предчистовая":
        label_add_minus = "✅ Допы -" if st.session_state["show_addons_minus"] else "Допы -"
        if cols[3].button(label_add_minus, key="btn_add_minus"):
            st.session_state["show_addons_minus"] = not st.session_state["show_addons_minus"]
            if st.session_state["show_addons_minus"]:
                st.session_state["show_addons_plus"] = False
    else:
        cols[3].write("")


# === Интерфейс ===
st.markdown("<p class='subheader'>🏡 Выберите проект дома</p>", unsafe_allow_html=True)
project = st.selectbox("", options=projects)

finish_buttons()

brick = st.radio("🧱 Тип кирпича", ["Силикатный", "Керамический"], horizontal=True)
payment = st.radio("💰 Способ оплаты", ["Наличные", "Ипотека"], horizontal=True)



# === ОТДЕЛЬНЫЕ СПИСКИ ДЛЯ ДОПОВ + и ДОПОВ - (разные словари!) ===
# Допы + (элементы, которые добавляют стоимость)
addons_plus = {
    "Штукатурка ручная": 110_000,
    "Штукатурка механизированная": 300_000,
    "Электрика (компл.)": 130_000,
    "Сантехника (компл.)": 210_000,
    "Механизированная стяжка": 100_000,
    "Септик": 60_000,
    "Утеплитель крыши": 50_000,
    "Газовый котел": 40_000,
    "Электрический котел": 20_000
}

# Допы - (элементы, которые отнимаются / корректируют стоимость при Предчистовая)
# значения — положительные, но в расчёте они будут вычитаться (мы добавляем отрицательное число)
addons_minus = {
    "Натяжные потолки": 40_000,
    "Штукатурка (выр-ся)": 75_000,
    "Электрика (урез.)": 70_000,
    "Сантехника (урез.)": 150_000,
    "Механизированная стяжка пола": 50_000,
    "Септик": 40_000,
    "М/п окна белый": 110_000,
    "М/п окна графит": 120_000,
    "Дверь террасная": 50_000,
    "Дверь входная": 15_000,
    "Газовый котел": 36_000,
    "Электрический котел": 15_000,
    "Радиаторы отопления": 19_000,
    "Крыша (металл)": 150_000,
    "Утеплитель крыши": 40_000,
    "Пенопласт стены": 5_000,
    "Тёплый пол": 20_000
}

# === Блок отображения допов в зависимости от режима ===
addons_sum = 0

if st.session_state.get("show_addons_plus", False):
    st.markdown("<p class='subheader'>🛠 Допы + (добавляются к сумме)</p>", unsafe_allow_html=True)
    # показать чекбоксы по колонкам (2 колонки)
    plus_names = list(addons_plus.items())
    for i in range(0, len(plus_names), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = i + j
            if idx < len(plus_names):
                name, price = plus_names[idx]
                key = f"plus_{name}"
                checked = cols[j].checkbox(f"{name} +{price:,} ₽".replace(",", " "), key=key)
                if checked:
                    addons_sum += price

if st.session_state.get("show_addons_minus", False):
    st.markdown("<p class='subheader'>🛠 Допы - (вычитаются из суммы)</p>", unsafe_allow_html=True)
    minus_names = list(addons_minus.items())
    for i in range(0, len(minus_names), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = i + j
            if idx < len(minus_names):
                name, price = minus_names[idx]
                key = f"minus_{name}"
                checked = cols[j].checkbox(f"{name} -{price:,} ₽".replace(",", " "), key=key)
                if checked:
                    addons_sum -= price  # отнимаем

# === Логистика ===
st.markdown("<p class='subheader'>🚚 Логистика (₽)</p>", unsafe_allow_html=True)
logistics = st.number_input("", min_value=0, step=50000, value=0, format="%d")

# === Расчёт финальной стоимости ===
if project and st.session_state.get("finish_choice") and brick and payment:
    try:
        price = data[project][st.session_state["finish_choice"]][brick][payment]
        if price:
            total = price + int(logistics) + addons_sum
            st.markdown(
                f"<div class='price-box'>💵 Предварительная стоимость: {total:,.0f} ₽</div>".replace(",", " "),
                unsafe_allow_html=True
            )
        else:
            st.warning("Не удалось определить цену по выбранным параметрам (возможно, в прайсе отсутствует нужная комбинация).")
    except Exception as e:
        st.error(f"Ошибка при расчёте: {e}")
else:
    st.info("Выберите проект и отделку (Черновая или Предчистовая), затем — допы (если нужно).")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>ℹ️ В будущем: логистика, регион, экспорт в Excel, визуализация плана.</p>", unsafe_allow_html=True)
