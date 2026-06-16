import streamlit as st
import json
import pytesseract
from fuzzywuzzy import process, fuzz
from PIL import Image

# 1. Đọc file dữ liệu (Đã thêm khiên bảo vệ strict=False để bỏ qua lỗi ký tự ẩn)
@st.cache_data
def load_db():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f, strict=False)

# 2. Hàm đọc chữ từ ảnh
def scan_image(image_file):
    img = Image.open(image_file).convert('L')
    text = pytesseract.image_to_string(img, lang='vie')
    return text.strip()

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Tra cứu 600 câu GPLX", page_icon="🚗")
st.title("🚗 Tra cứu đáp án thi lái xe")

try:
    db = load_db()
except Exception as e:
    st.error(f"Dữ liệu đang được tải hoặc có lỗi nhỏ: {e}")
    st.stop()

# Nút bật camera trên điện thoại
camera_image = st.camera_input("Bấm vào đây để chụp ảnh câu hỏi")

if camera_image is not None:
    with st.spinner('Đang đọc ảnh và tìm đáp án...'):
        scanned_text = scan_image(camera_image)
        
        if len(scanned_text) < 5:
            st.error("Không đọc được chữ. Vui lòng chụp gần và rõ nét hơn!")
        else:
            # Lọc danh sách câu hỏi an toàn (bỏ qua câu bị thiếu chữ 'question')
            questions_list = [item.get('question', '') for item in db if isinstance(item, dict) and item.get('question')]
            
            if not questions_list:
                st.error("Dữ liệu của bạn chưa có câu hỏi nào hợp lệ!")
            else:
                best_match, score = process.extractOne(scanned_text, questions_list, scorer=fuzz.token_set_ratio)
                
                if score > 60: 
                    for item in db:
                        if isinstance(item, dict) and item.get('question') == best_match:
                            st.success("🎉 ĐÃ TÌM THẤY ĐÁP ÁN!")
                            st.write(f"**Câu hỏi nhận diện được:** {item.get('question')}")
                            
                            correct_ans = item.get('correct_answer')
                            options = item.get('options', [])
                            
                            # Hiển thị đáp án an toàn
                            if correct_ans and isinstance(options, list) and len(options) >= correct_ans:
                                st.markdown(f"### 👉 ĐÁP ÁN ĐÚNG: Ý SỐ {correct_ans}")
                                st.info(f"{options[correct_ans - 1]}")
                            else:
                                st.markdown(f"### 👉 ĐÁP ÁN ĐÚNG: Ý SỐ {correct_ans}")
                            break
                else:
                    st.warning("Ảnh chụp bị mờ hoặc câu hỏi chưa có trong cơ sở dữ liệu. Vui lòng thử lại!")
