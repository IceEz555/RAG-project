import streamlit as st
from hf_integrations import analyze_image

def show_magic_fridge():
    st.title("📸 Magic Fridge")
    st.write("Take a photo of your fridge or ingredients, and I'll tell you what to cook!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Upload Photo")
        uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])

    with col2:
        if uploaded_file is not None:
            st.image(uploaded_file, caption='Your Ingredients', use_column_width=True)
            
            if st.button("🔍 Analyze Ingredients", type="primary"):
                with st.spinner("Analyzing..."):
                    image_bytes = uploaded_file.getvalue()
                    description = analyze_image(image_bytes)
                    
                    if "Error" in description:
                        st.error(description)
                    else:
                        st.success("Analysis Complete!")
                        st.markdown(f"**Found:** {description}")
                        
                        if "chat_history" not in st.session_state:
                            st.session_state["chat_history"] = []
                            
                        # Add to chat context
                        prompt = f"I have these ingredients: {description}. What can I cook with them?"
                        st.session_state["chat_history"].append({"role": "user", "content": prompt})
                        st.session_state["trigger_agent"] = prompt
                        
                        st.balloons()
                        st.info("Switched to Chat Bot to answer you!")
