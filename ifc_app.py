import streamlit as st
import ifcopenshell
import ifcopenshell.util.element
import tempfile
import os
import json

st.set_page_config(layout="wide")
st.title("🏗️ IFC 3D Viewer — визуализация, дерево, свойства и проверки")

# === Загрузка файла ===
uploaded_file = st.file_uploader("Загрузите IFC-файл", type=["ifc"])

if not uploaded_file:
    st.info("⬆ Пожалуйста, загрузите IFC-файл для начала работы")
    st.stop()

# === Сохраняем временно ===
temp_dir = tempfile.mkdtemp()
file_path = os.path.join(temp_dir, uploaded_file.name)
with open(file_path, "wb") as f:
    f.write(uploaded_file.getbuffer())

# === Открываем IFC ===
try:
    ifc = ifcopenshell.open(file_path)
except Exception as e:
    st.error(f"Не удалось открыть файл: {e}")
    st.stop()

# === Визуализация (IFC.js iframe) ===
st.subheader("🧱 3D-визуализация (IFC.js)")
viewer_html = f"""
<iframe
    src="https://ifcjs.github.io/ifcjs-crash-course/examples/01/index.html?file={uploaded_file.name}"
    width="100%"
    height="600px"
    style="border:1px solid #ccc; border-radius: 8px;"
></iframe>
<p style="color: gray; font-size: 0.8em;">Модель отображается через внешний IFC.js viewer</p>
"""
st.components.v1.html(viewer_html, height=620)

# === Дерево объектов ===
st.subheader("🌳 Дерево модели (объекты и их свойства)")

def build_tree(entity, level=0):
    indent = "—" * level
    name = getattr(entity, "Name", "[без имени]")
    if not name:
        name = "[без имени]"

    with st.expander(f"{indent} {entity.is_a()} — {name}", expanded=False):
        info = entity.get_info()
        for k, v in info.items():
            st.text(f"{k}: {v}")

        children = ifcopenshell.util.element.get_decomposition(entity)
        for child in children:
            build_tree(child, level + 1)

projects = ifc.by_type("IfcProject")
if not projects:
    st.error("❌ В файле нет IfcProject — не удалось построить дерево")
else:
    build_tree(projects[0])

# === Проверки ===
st.subheader("✅ Проверки модели")

# 1. Объекты без имени
no_name_objects = [e for e in ifc.by_type("IfcBuildingElement") if not getattr(e, "Name", None)]

# 2. Объекты без IFC-класса
no_class_objects = [e for e in ifc.by_type() if not e.is_a()]

# 3. Пустые свойства
empty_props = [e for e in ifc.by_type("IfcPropertySingleValue") if not e.NominalValue]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Без имени", len(no_name_objects))
    if no_name_objects:
        with st.expander("Список объектов без имени"):
            for obj in no_name_objects:
                st.text(f"#{obj.id()} — {obj.is_a()}")

with col2:
    st.metric("Без IFC-класса", len(no_class_objects))

with col3:
    st.metric("Пустые свойства", len(empty_props))
    if empty_props:
        with st.expander("Список пустых свойств"):
            for p in empty_props:
                st.text(f"#{p.id()} — {p.Name}")

st.success("Анализ завершён")

# === Завершение ===
if st.button("🔁 Очистить и загрузить другой файл"):
    st.experimental_rerun()
