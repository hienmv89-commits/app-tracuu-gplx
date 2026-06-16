import streamlit as st
import json
import pytesseract
from fuzzywuzzy import process, fuzz
from PIL import Image

# Đọc file dữ liệu câu hỏi
@st.cache_data
def load_db():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

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
    st.error("Không tìm thấy hoặc lỗi cấu trúc file data.json.")
    st.stop()

# Nút bật camera trên điện thoại
camera_image = st.camera_input("Bấm vào đây để chụp ảnh câu hỏi")

if camera_image is not None:
    with st.spinner('Đang đọc ảnh và tìm đáp án...'):
        scanned_text = scan_image(camera_image)
        
        if len(scanned_text) < 5:
            st.error("Không đọc được chữ. Vui lòng chụp gần và rõ nét hơn!")
        else:
            # BẢN NÂNG CẤP: Dò tìm an toàn, bỏ qua các câu bị lỗi cú pháp trong file JSON
            questions_list = [item['question'] for item in db if isinstance(item, dict) and 'question' in item]
            
            if not questions_list:
                st.error("Dữ liệu của bạn chưa có câu hỏi nào hợp lệ!")
            else:
                best_match, score = process.extractOne(scanned_text, questions_list, scorer=fuzz.token_set_ratio)
                
                if score > 60: 
                    for item in db:
                        if isinstance(item, dict) and item.get('question') == best_match:
                            st.success("🎉 ĐÃ TÌM THẤY ĐÁP ÁN!")
                            st.write(f"**Câu hỏi nhận diện được:** {item.get('question')}")
                            
                            # Kiểm tra an toàn cho đáp án
                            correct_ans = item.get('correct_answer')
                            options = item.get('options', [])
                            
                            if correct_ans and options:
                                st.markdown(f"### 👉 ĐÁP ÁN ĐÚNG: Ý SỐ {correct_ans}")
                                try:
                                    correct_text = options[correct_ans - 1]
                                    st.info(f"{correct_text}")
                                except:
                                    st.warning("Có lỗi nhỏ khi hiển thị chi tiết đáp án.")
                            else:
                                st.warning("Câu hỏi này trong dữ liệu của bạn đang bị thiếu đáp án!")
                            break
                else:
                    st.warning("Ảnh chụp bị mờ hoặc câu hỏi chưa có trong cơ sở dữ liệu. Vui lòng thử lại!")
