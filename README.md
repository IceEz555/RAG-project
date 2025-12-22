# 👨‍🍳 AI Cooking Assistant (RAG Project)

An intelligent cooking assistant powered by Google Gemini and Retrieval-Augmented Generation (RAG). This application can help you with cooking recipes, methods, and general kitchen tips, while maintaining a separate conversational context for general chit-chat.

## ✨ Features

- **Dual Agent System**:
    - **Cooking Agent**: Specialized in food and cooking queries, equipped with RAG knowledge base.
    - **General Agent**: Handles greetings and general conversation.
- **Smart Routing**: automatically routes user queries to the appropriate agent based on context.
- **Separate Memory Streams**: Uses distinct memory checkpoints for each agent, allowing disjoint conversations (Cooking vs. General) to coexist under the same user session.
- **RAG Capability**: Retrieves relevant documents from a local Vector Store to provide accurate cooking information.
- **Interactive UI**: Built with Streamlit for a chat-like experience.

## 📂 Project Structure

The source code has been modularized for better maintainability:

```text
src/
├── main_logic.py   # Core logic: Agent creation, Routing, and Execution flow (get_answer)
├── dependency.py   # Setup: Model initialization, Tools, Middleware, and Helpers
├── variables.py    # Configuration: System prompts and constants
├── cook-test.py    # Frontend: Streamlit user interface
└── style.css       # Styling: Custom CSS for the frontend
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google API Key (GEMINI)

### Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install langchain langchain-google-genai langgraph streamlit python-dotenv
    ```
3.  Create a `.env` file in the root directory and add your API key:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```

### Usage

Run the web application:

```bash
streamlit run src/cook-test.py
```

## 🧠 How it Works

1.  **Input**: User types a message in the chat interface.
2.  **Guardrails**: The system checks for unsafe content.
3.  **Routing**: The `RouteQuery` model decides if the question is "General" or "Cooking".
4.  **Execution**:
    - If **General**: The General Agent (Stateful) responds.
    - If **Cooking**: The Cooking Agent (Stateful + RAG) retrieves documents and responds.
5.  **Memory**: The system uses `thread_id="1"` but accesses different `InMemorySaver` instances depending on the active agent, ensuring context isolation.

## 🛠️ Customization

- **Prompts**: Edit `src/variables.py` to change system behaviors.
- **Tools**: Add new tools in `src/dependency.py`.
- **Logic**: Modify routing or agent config in `src/main_logic.py`.
