import streamlit as st
import numpy as np

def calculate_nmck(prices):
    n = len(prices)
    if n == 0:
        return None, None, None, "Введите хотя бы одну цену"

    mean_price = np.mean(prices)
    std_dev = np.std(prices, ddof=1)  # среднее квадратическое отклонение
    variation_coeff = (std_dev / mean_price) * 100 if mean_price != 0 else None

    return mean_price, std_dev, variation_coeff, None

st.title("Калькулятор НМЦК")

st.write("Добавьте цены от разных поставщиков по одной:")

# Инициализация списка цен в session_state
if 'prices' not in st.session_state:
    st.session_state.prices = []

# Инициализация поля ввода для новой цены
if 'new_price_input' not in st.session_state:
    st.session_state.new_price_input = ""

# Используем text_input для ввода новой цены
new_price_input = st.text_input("Введите цену", value=st.session_state.new_price_input)

# Обработка добавления новой цены
if st.button("Добавить цену"):
    if new_price_input:
        try:
            new_price = float(new_price_input)
            if new_price >= 0.01:  # Проверяем минимальную цену
                st.session_state.prices.append(new_price)
                st.session_state.new_price_input = ""  # Сброс поля ввода
            else:
                st.error("Цена должна быть не меньше 0.01")
        except ValueError:
            st.error("Пожалуйста, введите корректную цену.")

st.write("### Введенные цены:")
st.write(st.session_state.prices)

# Расчет НМЦК
if st.button("Рассчитать НМЦК"):
    if st.session_state.prices:
        mean_price, std_dev, variation_coeff, error = calculate_nmck(st.session_state.prices)

        if error:
            st.error(error)
        else:
            st.write(f"**Средняя цена:** {mean_price:.2f}")
            st.write(f"**Среднее квадратическое отклонение:** {std_dev:.2f}")
            st.write(f"**Коэффициент вариации:** {variation_coeff:.2f}%")

            if variation_coeff > 33:
                st.warning("Коэффициент вариации превышает 33%, возможны выбросы в данных!")
    else:
        st.error("Добавьте хотя бы одну цену для расчета.")
