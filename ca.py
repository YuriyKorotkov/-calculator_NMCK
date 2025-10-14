import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Калькулятор строительства дома", page_icon="🏡", layout="centered")

# --- Стили ---
st.markdown("""
<style>
body { background-color: #0f5d38; color: #ffffff !important; }
.stApp { background-color: #0f5d38 !important; padding: 30px; color: #ffffff !important; }
h1,h2,h3,h4,h5,h6,p,label,div,span { color: #ffffff !important; }
.stButton>button { background-color: #1b7c3e !important; color: #ffffff !important; border-radius: 10px !important; height: 3em; font-weight: 600; transition: 0.3s; }
.stButton>button:hover { background-color: #26a659 !important; transform: scale(1.05); }
.stSelectbox>div>div>div, .stMultiSelect>div>div>div, .stRadio>div>label>div, select, option, .stTextInput>div>div>input {
    background-color: #1a7a50 !important; color: #ffffff !important; border-radius: 8px !important; border: 1px solid #26a659 !important;
}
::placeholder { color: #eeeeee !important; }
</style>
""", unsafe_allow_html=True)

st.title("🏗️ Калькулятор стоимости строительства дома")

# --- Параметры дома ---
house_type = st.selectbox("Тип дома:", ["Кирпичный", "Газобетон", "Комбинированный (кирпич + газобетон)"])
floors = st.radio("Этажность:", ["Один этаж", "Полтора этажа", "Два этажа"])
region = st.selectbox("Регион:", ["Краснодар","Ростов","Динская","Старокорсунская","Елизаветинская","Северная","Калининская","Кореновск","Усть-Лабинск","Кущевская"])
project = st.selectbox("Проект:", ["Родимый","Семейный","Уют","Комфорт","Классик","Свой проект"])
area = st.number_input("Площадь дома (м²):", min_value=50, max_value=400, step=10) if project=="Свой проект" else {"Родимый":120,"Семейный":140,"Уют":100,"Комфорт":160,"Классик":180}[project]
windows = st.radio("Тип окон:", ["Классик","Утеплённые","Премиум"])
brick_type = st.selectbox("Тип кирпича:", ["Славянский","Силикатный","Керамический"])

# --- Расчёт ---
base_price = (6_500_000 + 12_000_000)/2
# этажность
base_price *= {"Один этаж":0.9,"Полтора этажа":1.0,"Два этажа":1.15}[floors]
# материал дома
base_price *= {"Газобетон":0.9,"Комбинированный (кирпич + газобетон)":1.05,"Кирпичный":1.1}[house_type]
# кирпич
base_price *= {"Славянский":1.0,"Силикатный":0.95,"Керамический":1.1}[brick_type]
# регион
base_price *= {"Краснодар":1.00,"Ростов":1.10,"Динская":1.05,"Старокорсунская":1.06,"Елизаветинская":1.07,"Северная":1.08,"Калининская":1.09,"Кореновск":1.10,"Усть-Лабинск":1.11,"Кущевская":1.12}[region]
# окна
base_price *= {"Классик":1.0,"Утеплённые":1.03,"Премиум":1.07}[windows]
# площадь
base_price *= (area/120)

st.divider()
st.subheader("💰 Примерная стоимость:")
st.success(f"{base_price:,.0f} ₽".replace(","," "))

# --- Генерация Excel ---
data = {
    "Параметр":["Тип дома","Этажность","Регион","Проект","Площадь","Тип окон","Тип кирпича","Итоговая стоимость"],
    "Выбор":[house_type,floors,region,project,f"{area} м²",windows,brick_type,f"{base_price:,.0f} ₽"],
    "Цена":["-","-","-","-","-","-","-",f"{base_price:,.0f} ₽"]
}
df = pd.DataFrame(data)
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name="Смета")
output.seek(0)

st.download_button("📄 Скачать Excel", data=output, file_name="Смета_дома.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Кнопка заказать звонок ---
phone = st.text_input("📞 Ваш номер для обратного звонка:")
if st.button("Заказать обратный звонок"):
    if phone.strip():
        st.success(f"Спасибо! Мы перезвоним вам на {phone}")
    else:
        st.error("Введите номер телефона")

# --- Кнопка Telegram ---
telegram_link = "https://t.me/ваш_бот"  # вставьте ссылку на своего бота
if st.button("💬 Telegram бот"):
    st.markdown(f"[Перейти в Telegram]({telegram_link})", unsafe_allow_html=True)
