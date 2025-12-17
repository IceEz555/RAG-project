import streamlit as st
from streamlit_chat import message
from RAG-Test.agent_service import getAnswer
# ตั้งค่า Streamlit page
st.set_page_config(page_title="Task AI Chatbot", page_icon="🤖", layout="centered")
# Custom CSS ให้ดู Modern เหมือนหน้าเว็บหลัก
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    h1 {
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    .stChatMessage {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("Task AI")
    st.caption("v1.0.0 (Prototype)")
    
    st.divider()
    
    st.subheader("💡 คำถามที่แนะนำ")
    st.markdown("""
    - สรุปสถานะโปรเจกต์ทั้งหมด
    - มีงานด่วนอะไรบ้าง?
    - ใครรับผิดชอบงานบ้าง?
    - งานที่เสร็จแล้วมีกี่งาน
    """)
    
    st.divider()
    
    if st.button("ล้างประวัติการสนทนา", type="primary"):
        st.session_state["chat_history"] = []
        st.rerun()

# Main Chat Interface
st.title("Task Assistant")
st.markdown("ถามข้อมูลเกี่ยวกับ **Projects**, **Tasks**, หรือ **Team Members** ได้เลยครับ")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "greeting_displayed" not in st.session_state:
    st.session_state["greeting_displayed"] = False
    
# Display chat history.
for chat in st.session_state["chat_history"]:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])
            
if not st.session_state["greeting_displayed"]:
    with st.chat_message("assistant"):
        st.markdown("Hi there! I am your Task Assistant. How can I help you today?")
    st.session_state["greeting_displayed"] = True

    # Accept user input.
if prompt := st.chat_input("Say something"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        response_origi = getAnswer(query=prompt)
        print("response_origi:", response_origi)
        answer_origi = response_origi
        answer_origi = 'Task Assistance : ' + answer_origi
        st.markdown(answer_origi)
        full_response = answer_origi
        st.session_state["chat_history"].append({"role": "assistant", "content": " "+full_response})