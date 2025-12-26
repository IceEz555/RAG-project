from st_chat_message import message
# from st_on_hover_tabs import on_hover_tabs # Removed custom tabs
from main_logic import get_answer, reset_token_counter
from magic_fridge import show_magic_fridge
import io
import streamlit as st
from st_on_hover_tabs import on_hover_tabs
import io
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
    tabs = on_hover_tabs(tabName=['Chat Bot', 'Recipe Search', 'Magic Fridge'],
                        iconName=['chat', 'search', 'camera'], default_choice=0)
    
    st.divider()
    
    show_sources = st.toggle("Sources", value=False)
    
    st.divider()
    
    # Token Usage Display
    if "token_stats" in st.session_state:
        stats = st.session_state["token_stats"]
        st.markdown(f"### 🔢 Token Usage")
        st.caption(f"Model: {stats.get('model', 'N/A')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Input", f"{stats['input_tokens']:,}")
            st.metric("Output", f"{stats['output_tokens']:,}")
        with col2:
            st.metric("Total", f"{stats['total_tokens']:,}", 
                     delta=f"{stats['session_count']} msgs")

    
    st.divider()
    if st.button("🗑️", help="Clear Chat"):
        st.session_state["chat_history"] = []
        st.session_state["greeting_displayed"] = False
        if "token_stats" in st.session_state:
            del st.session_state["token_stats"]
        reset_token_counter()  # Reset the global token counter
        st.rerun()

# Logic is already using 'tabs' variable, so no mapping needed.


# -------------------------------------------------
#  Chat Bot
# -------------------------------------------------
if tabs =='Chat Bot':
    st.title("AI Chef")
    st.write("You can chat with the AI here")

     # Initialise session state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "greeting_displayed" not in st.session_state:
        st.session_state["greeting_displayed"] = False


    # Display chat history with unique keys
    for i, chat in enumerate(st.session_state["chat_history"]):
        message(chat["content"], is_user=(chat["role"] == "user"), key=f"chat_msg_{i}")
    
    # Display greeting message (persisted)
    if not st.session_state["greeting_displayed"]:
        # Show greeting bubble
        message("Hi there! I'm your AI chef assistant. How can I help you today?")
        # Keep greeting in chat history so it stays visible
        st.session_state["chat_history"].append({"role": "assistant", "content": "Hi there! I'm your AI chef assistant. How can I help you today?"})
        st.session_state["greeting_displayed"] = True

    # -------------------------------------------------
    #  รับข้อความจากผู้ใช้
    # -------------------------------------------------
    if user_input := st.chat_input("Say something"):
        # show user input
        message(user_input, is_user=True)
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        
        # Generate AI response
        response, sources, token_stats = get_answer(query=user_input)
        
        # Update token stats in session state
        st.session_state["token_stats"] = token_stats

        # show AI response
        message(response, is_user=False, key="ai_response")
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": response}
        )

        if sources and show_sources:
            with st.expander("🔍 Retrieved Context (Sources)"):
                for i, source in enumerate(sources):
                    st.markdown(f"##### Retrive_content {i+1}")
                    
                    # Check if source is a Document object (has 'page_content' and 'metadata')
                    if hasattr(source, 'page_content') and hasattr(source, 'metadata'):
                        st.markdown("**Source:**")
                        st.json(source.metadata)
                        st.markdown("**Content:**")
                        st.text(source.page_content)
                    else:
                        # Fallback for string content
                        st.text(source)
                    st.divider()

    # Handle Auto-Trigger from Image Upload
    if "trigger_agent" in st.session_state:
        user_input = st.session_state.pop("trigger_agent")
        # We don't need to append to history again as it was done in the button callback
        # But we need to call logic
        response, sources, token_stats = get_answer(query=user_input)
        
        # Update token stats
        st.session_state["token_stats"] = token_stats
        
        message(response, is_user=False, key="ai_response_auto")
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": response}
        )
        st.rerun()


elif tabs == 'Recipe Search':
    st.title("🍳 Recipe Search & Import")
    st.write("Found a cool recipe online? Paste the link here to let me read it!")
    
    recipe_url = st.text_input("Paste Recipe URL (e.g., from AllRecipes, FoodNetwork)")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        st.write("")
        st.write("")
        read_btn = st.button("Read Recipe", type="primary")
    
    if read_btn:
        if recipe_url:
            with st.spinner("Reading recipe..."):
                from scraper import scrape_recipe
                result = scrape_recipe(recipe_url)
                
                if "Error" in result:
                    st.error(result)
                else:
                    st.success("Done!")
                    with st.expander("View Recipe Content", expanded=True):
                        st.markdown(result)
                    
                    if st.button("Save to Chat Context"):
                        st.session_state["chat_history"].append({"role": "user", "content": f"I found this recipe: {result}"})
                        st.session_state["chat_history"].append({"role": "assistant", "content": "Got it! I've memorized this recipe. Ask me anything about it."})
                        st.success("Saved! Switch to 'Chat Bot' to discuss it.")
        else:
            st.warning("Please enter a URL.")

elif tabs == 'Magic Fridge':
    show_magic_fridge()
    
    # Auto-switch if triggered
    if "trigger_agent" in st.session_state:
        # Optional: Force switch tab visually? 
        # Streamlit re-run might reset standard widgets unless controlled. 
        # But user can manually click 'Chat Bot' after seeing the success message.
        pass
