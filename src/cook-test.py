# from  import getAnswer
import streamlit as st
from st_chat_message import message
from st_on_hover_tabs import on_hover_tabs
from st_on_hover_tabs import on_hover_tabs
import streamlit as st

st.set_page_config(layout="wide", page_title="AI Cooking Assistant", page_icon="👨‍🍳")
st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div class="sub-header-content">
    <h1 class="header-title">👨‍🍳 AI Cooking Assistant</h1>
    <p class="header-subtitle"> Welcome to our AI Cooking Assistant! </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    tabs = on_hover_tabs(tabName=['Chat Bot', 'Money'],
                        iconName=['chat', 'money'], default_choice=0)

# Chat Bot
if tabs =='Chat Bot':
    st.title("AI Chef")
    st.write("You can chat with the AI here")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "greeting_displayed" not in st.session_state:
        st.session_state["greeting_displayed"] = False

    # Display chat history
    for chat in st.session_state["chat_history"]:
        with message(chat["role"]):
            st.markdown(chat["content"])
    # Display greeting message
    if not st.session_state["greeting_displayed"]:
        message("Hi there! I'm your AI chef assistant. How can I help you today?")
        st.session_state["greeting_displayed"] = True

    # Get user input
    if user_input := st.chat_input("Say somthing"):     
        with message("user"):
            st.markdown(user_input)
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        # Generate AI response
        # with message("assistant"):
        #     response_origi = getAnswer(query=user_input)
        #     print("Response_origi: ", response_origi)
        #     answer_origi = response_origi
        #     awnser_origi = "Original answer: " + answer_origi
        #     st.markdown(awnser_origi)


elif tabs == 'Money':
    st.title("Paper")
    st.write('Name of option is {}'.format(tabs))

