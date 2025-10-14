import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Калькулятор стоимости дома", layout="centered")

# === Стили ===
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #fff8e1, #ffecb3); color: #000; }
    h1 { color:#000; font-weight:700; }
    .subheader { color:#009639; font-weight:700; margin-bottom:0.4em; }
    /* Кнопки выбора компактнее */
    div[data-testid="stHorizontalBlock"] button {
        margin: 3px 4px;
        border-radius: 8px;
        border: 1px solid #009639 !important;
        font-weight: 600;
        padding: 0.35em 0.9em;
    }
    /* Активная кнопка (показываем через префикс "✅" в тексте, поэтому только стили hover) */
    div[data-testid="stHorizontalBlock"] button:hover {
        background-color: #cde9d9 !important;
    }
    .stButton>button { background-color:#009639 !important; color:white !important; border-radius:8px !important; }
    .price-box {
        background-color:#e6f4ea; color:#000; padding:10px; border-radius:6px; font-size:20px; font-weight:700; text-align:center; border:2px solid #009639;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏠 Калькулятор стоимости дома — СК «Дом на Века»</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Выберите параметры дома для расчёта предварительной стоимости</p>", unsafe_allow_html=True)

# === Загрузка файла ===
@st.cache_data
def load_data(file_path="Прайс ДНВ 2025 (13 проектов).xlsx"):
    df = pd.read_excel(file_path, header=None)
    df = df.dropna(how="all")
    return df

df = load_data()

# === Вспомогательные парсеры ===
def split_lines(cell):
    """Возвращает список непустых строк в ячейке (убирает неразрывные пробелы в начале/конце)."""
    if cell is None or (isinstance(cell, float) and math.isnan(cell)):
        return []
    s = str(cell).replace("\r", "\n")
    # заменяем неразрывные пробелы на обычные, не трогаем цифры пока
    s = s.replace("\xa0", " ")
    parts = [p.strip() for p in s.split("\n") if p.strip() != ""]
    return parts

def to_int_from_str(s):
    """Убирает пробелы и символы и пытается вернуть int, иначе None."""
    if s is None:
        return None
    t = str(s).replace("\xa0", "").replace(" ", "").replace("₽", "").strip()
    try:
        return int(t)
    except Exception:
        return None

def get_price_from_cells(cell, next_cell, payment):
    """
    Логика:
    - если в cell несколько строк -> верхняя = наличные, нижняя = ипотека (берём last для ипотека).
    - если в cell одна строка:
        - для наличных: берём её.
        - для ипотеки: если next_cell содержит строк(ы), берём первую строку next_cell (fallback).
    - если cell пустой, смотрим в next_cell аналогично.
    """
    parts = split_lines(cell)
    if parts:
        if len(parts) >= 2:
            # многострочная: 1st = наличные, last = ипотека
            return to_int_from_str(parts[0]) if payment == "Наличные" else to_int_from_str(parts[-1])
        else:
            # одна строка
            if payment == "Наличные":
                return to_int_from_str(parts[0])
            else:
                # ипотека — попробуем взять из той же строки, если там явно указана ипотека (редко),
                # иначе возьмём из next_cell (fallback)
                # Попробуем интерпретировать возможные разделители внутри строки (если есть "/")
                # но основная стратегия: fallback to next_cell
                next_parts = split_lines(next_cell)
                if next_parts:
                    return to_int_from_str(next_parts[0])
                else:
                    return None
    else:
        # cell пустой -> смотрим в next_cell
        next_parts = split_lines(next_cell)
        if not next_parts:
            return None
        return to_int_from_str(next_parts[0]) if payment == "Наличные" else to_int_from_str(next_parts[-1])

# === Сбор данных в структуру ===
project_rows = df[df[0].astype(str).str.contains("«", na=False)]
projects = project_rows[0].tolist()

data = {}
for i, row in project_rows.iterrows():
    project_name = str(row[0]).strip()
    next_row = df.iloc[i + 1] if i + 1 < len(df) else None

    data[project_name] = {}
    # столбцы: 1 - Черновая силикатный, 2 - Черновая керамический, 3 - Предчистовая силикатный, 4 - Предчистовая керамический
    for finish_type, col_start in zip(["Черновая", "Предчистовая"], [1, 3]):
        # получаем ячейки текущей строки и ячейки следующей строки (если есть)
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

# === Удобные кнопки выбора (через st.session_state) ===
def option_row(label, options, key):
    st.markdown(f"<p class='subheader'>{label}</p>", unsafe_allow_html=True)
    cols = st.columns(len(options))
    if key not in st.session_state:
        st.session_state[key] = options[0]
    for i, opt in enumerate(options):
        selected = (st.session_state[key] == opt)
        # отображаем галочку у активной опции для наглядности
        label_btn = f"✅ {opt}" if selected else opt
        if cols[i].button(label_btn, key=f"{key}_{i}"):
            st.session_state[key] = opt
    return st.session_state[key]

# === Интерфейс ===
project = st.selectbox("🏡 Выберите проект дома", options=projects)
finish = option_row("🎨 Тип отделки", ["Черновая", "Предчистовая"], "finish")
brick = option_row("🧱 Тип кирпича", ["Силикатный", "Керамический"], "brick")
payment = option_row("💰 Способ оплаты", ["Наличные", "Ипотека"], "payment")

# === Расчёт и вывод ===
if project and finish and brick and payment:
    try:
        price = data[project][finish][brick][payment]
        if price:
            st.markdown(f"<div class='price-box'>💵 Предварительная стоимость: {price:,} ₽</div>".replace(",", " "), unsafe_allow_html=True)
        else:
            st.warning("Не удалось определить цену по выбранным параметрам (возможно, в прайсе отсутствует нужная комбинация).")
    except Exception as e:
        st.error(f"Ошибка при расчёте: {e}")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>ℹ️ В будущем: логистика, регион, экспорт в Excel.</p>", unsafe_allow_html=True)
