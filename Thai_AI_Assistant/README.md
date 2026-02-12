# 🇹🇭 Local Thai AI Assistant (Hybrid Input)

โปรเจกต์นี้คือ AI Assistant ที่ทำงานบนคอมพิวเตอร์ของคุณ 100% (Local) โดยไม่ต้องใช้อินเทอร์เน็ตในการประมวลผล (ยกเว้นตอนโหลดโมเดลครั้งแรก) รองรับทั้งการพิมพ์คุยและการพูดคุยภาษาไทยแบบครบวงจร

## 📋 Prerequisites (สิ่งที่ต้องมี)

### 1. ติดตั้ง Python Library

รันคำสั่งนี้ใน Terminal เพื่อติดตั้งทุกอย่างที่จำเป็น:

```bash
pip install -r requirements.txt
```

_Tip: แนะนำให้สร้าง Virtual Environment ก่อน (เช่น `python -m venv venv` แล้ว activate)_

### 2. ติดตั้ง Ollama (สำหรับรัน LLM)

1. ดาวน์โหลดและติดตั้ง [Ollama](https://ollama.com/)
2. เปิด Terminal แล้วดึงโมเดลที่ต้องการมาลงเครื่อง:
   ```bash
   ollama pull llama3
   ollama pull typhoon-v1.5-8b-instruct  # แนะนำสำหรับภาษาไทย
   ```
3. รัน Server ทิ้งไว้ (ปกติ Ollama จะทำงานอยู่แล้วหลังติดตั้ง)

---

## 🚀 วิธีรันโปรแกรม

1. เปิด Terminal ในโฟลเดอร์นี้
2. รันคำสั่ง:
   ```bash
   streamlit run app.py
   ```
3. Browser จะเปิดขึ้นมาพร้อมใช้งาน!

---

## 🧩 Code Explanation (อธิบายโค้ด)

โปรแกรมนี้แบ่งการทำงานออกเป็น 3 ส่วนหลัก (Pipeline):

### 1. 👂 Speech-to-Text (STT) - หูของ AI

เราใช้ `faster-whisper` ซึ่งเป็นเวอร์ชันที่ปรับจูนมาให้เร็วกว่า Whisper ปกติ

- **Code**: `transcribe_audio(audio_bytes)`
- **หน้าที่**: รับไฟล์เสียงจากการอัด -> แปลงเป็นข้อความภาษาไทย
- **Settings**: ใช้ Info `model_size='small'` เพื่อความเร็ว (ถ้าการ์ดจอแรงปรับเป็น 'medium' หรือ 'large' ได้)

### 2. 🧠 LLM (Brain) - สมองของ AI

เราใช้ `ollama` เป็นตัวคุยกับโมเดล

- **Code**: `query_ollama(prompt)`
- **หน้าที่**: ส่งข้อความที่เราพูด/พิมพ์ ไปหาโมเดล (เช่น Llama3) แล้วรับคำตอบกลับมา
- **Tip**: ถ้าอยากให้เก่งไทย แนะนำโมเดล `typhoon` หรือ `openthaigpt` ที่รันบน Ollama ได้

### 3. 🗣️ Text-to-Speech (TTS) - ปากของ AI

เราใช้ `transformers` กับโมเดล `facebook/mms-tts-tha`

- **Code**: `text_to_speech(text)`
- **หน้าที่**: แปลงข้อความคำตอบ -> ไฟล์เสียง (Waveform)
- **การทำงาน**: ใช้ VITS Model ซึ่งเสียงค่อนข้างธรรมชาติและทำงานเร็วพอสมควรบน CPU

### 4. 💻 UI (Streamlit)

ใช้ `streamlit` สร้างหน้าเว็บง่ายๆ

- **Hybrid Input**: มี Tab ให้เลือก "Text" หรือ "Voice"
- **Session State**: เก็บประวัติการคุย (`st.session_state.messages`) เพื่อให้คุยต่อเนื่องได้

---

## 🛠️ Troubleshooting (ปัญหาที่พบบ่อย)

### 1. อัดเสียงไม่ได้/ไม่ขึ้น

- **สาเหตุ**: Browser อาจบล็อกการเข้าถึงไมโครโฟน
- **วิธีแก้**: กดอนุญาต (Allow) ที่มุมขวาบนของ URL bar หรือลองเปลี่ยน Browser (Chrome/Edge แนะนำสุด)

### 2. ช้ามาก

- **สาเหตุ**: รันบน CPU ล้วนๆ อาจจะหน่วงตอนถอดเสียง (STT) หรือสร้างเสียง (TTS)
- **วิธีแก้**:
  - ลดขนาดโมเดล Whisper เป็น `tiny`
  - ใช้ GPU (ต้องลง PyTorch เวอร์ชัน CUDA)

### 3. Ollama Error

- **สาเหตุ**: ลืมเปิด Ollama หรือยังไม่ได้โหลดโมเดล
- **วิธีแก้**: พิมพ์ `ollama list` ใน terminal เพื่อเช็คว่ามีโมเดลไหม ถ้าไม่มีให้ `ollama pull llama3`

### 4. ภาษาไทยเป็นต่างดาว

- **วิธีแก้**: ส่วนใหญ่ `faster-whisper` และ `mms-tts` รองรับไทยดีอยู่แล้ว แต่ถ้า LLM ตอบมั่ว ให้ลองเปลี่ยน Prompt หรือเปลี่ยนโมเดลเป็นตัวที่เก่งไทย (Typhoon)
