# 🏗️ System Architecture Documentation (RAG-Project)

## 1. Project Overview
This project is an **AI-powered Smart Cooking Assistant** that combines:
1.  **RAG (Retrieval-Augmented Generation)**: To answer cooking questions using a specific knowledge base (Vector Store).
2.  **Visual Analysis (Magic Fridge)**: To identify ingredients from refrigerator photos.
3.  **Agentic Workflow**: To route user queries to the appropriate expert (General Chat vs. Cooking Expert).

---

## 2. System Components
The system is built with **Python**, **Streamlit**, **LangChain**, and **Hugging Face Transformers**.

### 📁 Directory Structure & Key Files
*   `src/cook-test.py`: **Frontend Entry Point**. Main Streamlit application file handling the Chat UI.
*   `src/magic_fridge.py`: **Image UI Module**. Handles image upload and interaction for the "Magic Fridge" feature.
*   `src/hf_integrations.py`: **Visual AI Module**. Uses local Hugging Face models (VQA) to analyze images.
*   `src/main_logic.py`: **Core Logic**. Handles request routing, agent execution, and response generation.
*   `src/dependency.py`: **Configuration & Tools**. Initializes models, loads the Vector Store, and defines RAG tools.

---

## 3. Data Flow Pipelines

### 🟢 A. Chat Pipeline (Text Query)
When a user types a message in the chat:
1.  **User Input**: Text is sent from `cook-test.py`.
2.  **Safety Check**: `main_logic.safety_check()` filters for dangerous keywords.
3.  **Routing**: `llm_router` (Gemini) decides the intent:
    *   **General Topic** → Routes to `General Agent`.
    *   **Cooking Topic** → Routes to `Cooking Agent`.
4.  **Agent Execution**:
    *   **General Agent**: Chats normally using Gemini.
    *   **Cooking Agent**: Can call `retrive_context` tool to specific cooking knowledge from `Vector_Store_RAG`.
5.  **Summarization/Response**: The agent generates a final answer, which is sent back to the UI.

### 🔵 B. Magic Fridge Pipeline (Image Query)
When a user uploads a photo:
1.  **Upload**: Image is processed in `magic_fridge.py`.
2.  **Analysis**: `analyze_image()` in `hf_integrations.py` is called.
3.  **Model Inference**:
    *   Uses **Salesforce/blip-vqa-base** (Visual Question Answering).
    *   Asks the specific question: *"What food items are in the picture?"*
    *   Runs locally via `transformers` (using GPU if available, else CPU).
4.  **Context Injection**: The identified ingredients (e.g., "eggs, milk") are converted into a text prompt.
5.  **Agent Handoff**: The text prompt ("I have these ingredients...") is sent to the **Chat Pipeline** (See A) effectively jumping to the Cooking Agent to suggest recipes.

---

## 4. Technical Details

### 🧠 AI Models Used
| Purpose | Model Name | Source |
| :--- | :--- | :--- |
| **Chat & Routing** | `gemini-2.5-flash-lite` | Google GenAI API |
| **Embeddings** | `gemini-embedding-001` | Google GenAI API |
| **Image Analysis** | `Salesforce/blip-vqa-base` | Local (Hugging Face) |

### 🗄️ Database (RAG)
*   **Type**: Vector Store (InMemory)
*   **Path**: `../Vector_Store_RAG`
*   **Function**: Stores embeddings of cooking documents/recipes to allow the AI to "read" from a custom knowledge base.

---

## 5. Troubleshooting Common Issues
*   **Image Analysis Failed**: Ensure `pytorch` is installed and compatible with your GPU. The first run requires downloading ~1GB model files.
*   **Vector Store Warning**: If `Vector_Store_RAG` folder is missing, the RAG tool will likely fail or return empty results. Ensure you run the ingestion script (if available) first.
*   **Library Errors**: Recent versions of `transformers` require secure usage of `pickle`. We use `safetensors` or specific model classes (`BlipForQuestionAnswering`) to handle this.
