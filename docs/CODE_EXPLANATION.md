# 📖 Codebase Explanation

This document provides a detailed breakdown of each source file in the `src/` directory, explaining its purpose, key functions, and how it fits into the overall system.

---

## 🖥️ Frontend & UI

### 1. `src/cook-test.py`
**Purpose:** The entry point of the Streamlit application. It handles the main UI layout, chat interface, and sidebar.

*   **Key Logic:**
    *   Initializes `session_state` to store chat history (`messages`), thread ID, and active agent status.
    *   **Sidebar**: Displays the "Magic Fridge" section (imports `show_magic_fridge`) and "Vector Store Management" (imports `rebuild_vector_store`).
    *   **Chat Interface**: Renders chat bubbles for user and assistant.
    *   **Input Handling**: Captures `st.chat_input`, calls `get_answer` from `main_logic.py`, and displays the result text + source documents (if provided).

### 2. `src/magic_fridge.py`
**Purpose:** A UI module specifically for the "Magic Fridge" feature.

*   **Key Functions:**
    *   `show_magic_fridge()`: Renders the file uploader for images.
    *   **Interaction**: When an image is uploaded and "Analyze" is clicked, it calls `analyze_image` from `hf_integrations.py`.
    *   **Agent Trigger**: Takes the results (ingredients list) and automatically injects a prompt into the chat state (`st.session_state["trigger_agent"]`) to switch the active view to the Chat Bot.

### 3. `src/style.css`
**Purpose:** Contains custom CSS to beautify the Streamlit interface (e.g., custom colors for chat bubbles, hiding default menus).

---

## 🧠 Core Logic & AI

### 4. `src/main_logic.py`
**Purpose:** The "Brain" of the application. It orchestrates the AI agents, routing, and safety checks.

*   **Key Components:**
    *   **`RouteQuery` (Class)**: A Pydantic model used by the LLM to decide if a question is "general" or "cooking".
    *   **`route_question(query)`**: Uses Gemini to classify the user's intent.
    *   **`create_agent()`**: (Imported) Creates the LangChain agents.
    *   **`general_agent`**: Instance of the agent for chit-chat.
    *   **`cooking_agent`**: Instance of the agent equipped with `retrive_context` tool.
    *   **`get_answer(query)`**: The main function called by the frontend. It logs inputs, runs safety checks, routes the query, executes the correct agent, formats sources, and returns the final answer.

### 5. `src/hf_integrations.py`
**Purpose:** Handles local Computer Vision tasks using Hugging Face Transformers.

*   **Key Logic:**
    *   **Model Loading**: Downloads and loads `Salesforce/blip-image-captioning-large` onto the CPU or GPU.
    *   **`analyze_image(image_bytes)`**:
        *   Converts raw image bytes to a PIL Image.
        *   Constructs a prompt (`"fresh food ingredients on a table including "`) to guide the model.
        *   Uses `model.generate()` with Nucleus Sampling/Beam Search to generate a detailed text description of the food items.

---

## ⚙️ Configuration & Tools

### 6. `src/dependency.py`
**Purpose:** Sets up the infrastructure and external dependencies.

*   **Key Initialization:**
    *   Loads Environment Variables (`.env`).
    *   Initializes Gemini Chat Models (`init_chat_model`) and Embeddings (`GoogleGenerativeAIEmbeddings`).
    *   Loads the Vector Store (`InMemoryVectorStore`).
*   **Key Tools:**
    *   **`@tool retrive_context(query)`**: Performs a similarity search in the Vector Store to find relevant cooking documents.
*   **Middleware**:
    *   `SimpleLoggingMiddleware`: Logs chat activity to the console.
    *   `safety_check`: Basic keyword filter (e.g., preventing violent content).

### 7. `src/variables.py`
**Purpose:** Stores constant strings like System Prompts to keep the code clean.

*   **Variables:**
    *   `system_prompt`: Instructions for the Cooking Agent (Personalities, Rules).
    *   `general_system_prompt`: Instructions for the General Agent.

---

## 🛠️ Utilities & Data Processing

### 8. `src/rebuild_store.py`
**Purpose:** A script/module to manage the Knowledge Base (Vector Store).

*   **Key Functions:**
    *   `rebuild_vector_store()`:
        *   Reads text files from the `data/` directory.
        *   Splits text into chunks using `RecursiveCharacterTextSplitter`.
        *   Converts chunks into embeddings.
        *   Saves the new Vector Store to `Vector_Store_RAG`.
    *   This is crucial for updating the AI's knowledge with new recipes.

### 9. `src/scraper.py`
**Purpose:** A utility script to gather data from the web (Web Scraping).

*   **Usage**: Can be run to scrape recipes from websites and save them into `data/` to be ingested by `rebuild_store.py`.
