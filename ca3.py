import re
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Калькулятор стоимости дома", layout="centered")

# === Стили ===
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff8e1, #ffecb3);
    color: #000; 
    font-family: 'Segoe UI', sans-serif;
}
/* Заголовки — читаемый зелёный */
h1 { color:#009639; font-weight:800; font-size:2rem; text-align:center; margin-bottom:0.5em; }
.subheader { color:#009639; font-weight:700; font-size:1.1rem; margin-bottom:0.5em; }

/* Кнопки и элементы выбора */
div[data-testid="stHorizontalBlock"] button {
    margin: 3px 4px;
    border-radius:12px;
    border:1px solid #009639;
    font-weight:600;
    padding:0.5em 1.2em;
    transition: all 0.25s ease;
    background-color:#e6f4ea;
    color:#009639;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
div[data-testid="stHorizontalBlock"] button:hover {
    transform: scale(1.05);
    background-color:#cde9d9 !important;
}

/* Выбранная кнопка (визуализация через префикс "✅") */
.selected-btn {
    background: linear-gradient(135deg, #009639, #007f2f) !important;
    color:white !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.3);
    border: 1px solid #006622 !important;
}

/* Кнопка расчёта */
.stButton>button {
    background: linear-gradient(135deg, #009639, #007f2f) !important;
    color:white !important; border-radius:12px !important; font-weight:700 !important;
    padding:0.6em 1.5em; box-shadow:0 4px 12px rgba(0,0,0,0.2);
    transition: all 0.25s ease;
}
.stButton>button:hover { background: linear-gradient(135deg, #007f2f, #005f20) !important; transform: scale(1.05); }

/* Результат */
.price-box {
    background: linear-gradient(135deg, #e6f4ea, #d0efd6);
    color:#000; padding:15px; border-radius:12px; font-size:1.5rem;
    font-weight:700; text-align:center; border:2px solid #009639;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# === Заголовок ===
st.markdown("<h1>🏠 Калькулятор стоимости дома — СК «Дом на Века»</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Выберите параметры дома для расчёта предварительной стоимости</p>", unsafe_allow_html=True)

# === Загрузка данных ===
@st.cache_data
def load_data(file_path="Прайс ДНВ 2025 (13 проектов).xlsx"):
    df = pd.read_excel(file_path, header=None)
    df = df.dropna(how="all")
    return df

df = load_data()

# === Парсеры ===
def split_lines(cell):
    if cell is None or (isinstance(cell, float) and math.isnan(cell)):
        return []
    s = str(cell).replace("\r", "\n").replace("\xa0", " ")
    parts = [p.strip() for p in s.split("\n") if p.strip() != ""]
    return parts

def to_int_from_str(s):
    """Надёжно извлекает цифры и возвращает int. Работает и для чисел (int/float) и для строк с текстом."""
    if s is None:
        return None
    if isinstance(s, (int, float)) and not (isinstance(s, float) and math.isnan(s)):
        return int(s)
    digits = re.sub(r'\D', '', str(s))
    if digits == "":
        return None
    try:
        return int(digits)
    except:
        return None

def get_price_from_cells(cell, next_cell, payment):
    """
    Правила:
    - Если в ячейке несколько строк: верхняя = наличные, нижняя(последняя) = ипотека.
    - Если в ячейке одна строка:
        - для наличных: берём её.
        - для ипотеки: fallback — берём первую строку из next_cell (если есть).
    - Если ячейка пустая — смотрим в next_cell аналогично.
    """
    parts = split_lines(cell)
    if parts:
        if len(parts) >= 2:
            return to_int_from_str(parts[0]) if payment == "Наличные" else to_int_from_str(parts[-1])
        else:
            if payment == "Наличные":
                return to_int_from_str(parts[0])
            next_parts = split_lines(next_cell)
            if next_parts:
                return to_int_from_str(next_parts[0])
            return None
    next_parts = split_lines(next_cell)
    if not next_parts:
        return None
    return to_int_from_str(next_parts[0]) if payment == "Наличные" else to_int_from_str(next_parts[-1])

# === Сбор данных ===
# Ищем только строки, где проект начинается с кавычки «
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

# === Компоненты интерфейса (без изменений логики) ===
def option_row(label, options, key):
    st.markdown(f"<p class='subheader'>{label}</p>", unsafe_allow_html=True)
    cols = st.columns(len(options))
    if key not in st.session_state:
        st.session_state[key] = options[0]
    for i, opt in enumerate(options):
        selected = (st.session_state[key] == opt)
        btn_label = f"✅ {opt}" if selected else opt
        if cols[i].button(btn_label, key=f"{key}_{i}"):
            st.session_state[key] = opt
    return st.session_state[key]

# === Интерфейс ===
st.markdown("<p class='subheader'>🏡 Выберите проект дома</p>", unsafe_allow_html=True)
project = st.selectbox("", options=projects)

finish = option_row("🎨 Тип отделки", ["Черновая", "Предчистовая"], "finish")
brick = option_row("🧱 Тип кирпича", ["Силикатный", "Керамический"], "brick")
payment = option_row("💰 Способ оплаты", ["Наличные", "Ипотека"], "payment")

# === Новое поле логистики (включено по твоей просьбе ранее) ===
st.markdown("<p class='subheader'>🚚 Логистика (₽)</p>", unsafe_allow_html=True)
logistics = st.number_input("", min_value=0, step=1000, value=0, format="%d")


# === Расчёт и вывод ===
if project and finish and brick and payment:
    try:
        price = data[project][finish][brick][payment]
        if price:
            total = price + int(logistics)
            st.markdown(f"<div class='price-box'>💵 Предварительная стоимость: {total:,} ₽</div>".replace(",", " "), unsafe_allow_html=True)
        else:
            st.warning("Не удалось определить цену по выбранным параметрам (возможно, в прайсе отсутствует нужная комбинация).")
    except Exception as e:
        st.error(f"Ошибка при расчёте: {e}")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>ℹ️ В будущем: логистика, регион, экспорт в Excel.</p>", unsafe_allow_html=True)
