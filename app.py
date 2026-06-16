import streamlit as st
import json
import cv2
import numpy as np
import pytesseract
from fuzzywuzzy import process, fuzz
from PIL import Image

# Đọc file dữ liệu
@st.cache_data
def load_db():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Hàm đọc chữ từ ảnh
def scan_image(image_file):
    img = Image.open(image_file)
    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    # Tesseract trên server Linux đã được cài sẵn
    text = pytesseract.image_to_string(gray, lang='vie')
    return text.strip()

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Tra cứu 600 câu GPLX", page_icon="🚗")
st.title("🚗 Tra cứu đáp án thi lái xe")

db = load_db()

# Nút bật camera trên điện thoại
camera_image = st.camera_input("Bấm vào đây để chụp ảnh câu hỏi")

if camera_image is not None:
    with st.spinner('Đang đọc ảnh và tìm đáp án...'):
        scanned_text = scan_image(camera_image)
        
        if len(scanned_text) < 5:
            st.error("Không đọc được chữ. Vui lòng chụp gần và rõ nét hơn!")
        else:
            # So sánh với dữ liệu
            questions_list = [item['question'] for item in db]
            best_match, score = process.extractOne(scanned_text, questions_list, scorer=fuzz.token_set_ratio)
            
            if score > 60: # Khớp trên 60%
                for item in db:
                    if item['question'] == best_match:
                        st.success("🎉 ĐÃ TÌM THẤY ĐÁP ÁN!")
                        st.write(f"**Câu hỏi nhận diện được:** {item['question']}")
                        st.markdown(f"### 👉 ĐÁP ÁN ĐÚNG: Ý SỐ {item['correct_answer']}")
                        correct_text = item['options'][item['correct_answer'] - 1]
                        st.info(f"{correct_text}")
                        break
            else:
                st.warning("Ảnh chụp bị mờ hoặc câu hỏi không có trong cơ sở dữ liệu. Vui lòng thử lại!")