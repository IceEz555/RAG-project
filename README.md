# 👨‍🍳 AI Cooking Assistant & Magic Fridge 📸

Welcome to the **AI Cooking Assistant**! This project combines **GenAI (Gemini)**, **RAG (Retrieval-Augmented Generation)**, and **Computer Vision (Hugging Face)** to create a smart kitchen companion. It can chat about recipes, answer cooking questions from a knowledge base, and even analyze photos of your fridge to suggest menus!

---

## ✨ Key Features

1.  **🤖 Intelligent Chatbot (Dual Agent System)**
    *   **Cooking Agent**: An expert chef powered by RAG. It retrieves information from a custom knowledge base (Vector Store) to give accurate recipe advice.
    *   **General Agent**: A friendly assistant for greetings and chit-chat.
    *   **Smart Routing**: The system automatically detects your intent and switches between agents seamlessly.

2.  **📸 Magic Fridge (Image Recognition)**
    *   Upload a photo of your refrigerator or ingredients.
    *   The system uses **Local AI (Hugging Face Transformers)** to identify food items (e.g., "eggs, milk, carrots").
    *   It then automatically prompts the Cooking Agent to suggest recipes based on those ingredients!

3.  **🧠 Memory & Context**
    *   Remembers your conversation history using separated memory streams for general chat and cooking tasks.

---

## 🛠️ Prerequisites

Before you begin, make sure you have:
*   **Python 3.9+** installed.
*   **Google API Key** (for Gemini Models).
*   *(Optional)* **NVIDIA GPU** with CUDA support (for faster local image analysis).

---

## 🚀 Installation Guide

### 1. Clone the Repository
```bash
git clone <repository_url>
cd RAG-project
```

### 2. Install Dependencies
Run the following command to install all required libraries:
```bash
pip install streamlit langchain langchain-google-genai langgraph python-dotenv
pip install transformers torch pillow sentencepiece protobuf
```
*> Note: If you want to use GPU, make sure to install the correct version of PyTorch from [pytorch.org](https://pytorch.org/get-started/locally/).*

### 3. Setup Configuration
Create a `.env` file in the root directory (or rename `.env.example` -> `.env`) and add your keys:
```env
GOOGLE_API_KEY=your_google_api_key_here
HF_TOKEN=your_huggingface_token_here (optional, for some gated models)
```

---

## 🎮 How to Run

Start the web application using Streamlit:
```bash
streamlit run src/cook-test.py
```
This will open the app in your default web browser (usually at `http://localhost:8501`).

---

## 📁 Project Structure

```text
RAG-project/
├── data/                   # Raw text data for the knowledge base
├── src/                    # Source code
│   ├── cook-test.py        # 🖥️ Main Frontend (Streamlit)
│   ├── magic_fridge.py     # 📸 Image Analysis UI Module
│   ├── hf_integrations.py  # 🖼️ Computer Vision Logic (Hugging Face)
│   ├── main_logic.py       # 🧠 AI Brain (Agents, Routing, Safety)
│   ├── dependency.py       # ⚙️ Configuration & Tools (Vectors, Middleware)
│   └── variables.py        # 📝 Prompts & Constants
├── Vector_Store_RAG/       # 🗄️ Database (Embeddings)
└── SYSTEM_ARCHITECTURE.md  # 🏗️ Technical Documentation
```

---

## 🧩 Troubleshooting

**1. Image Analysis is slow?**
*   The system runs the Vision model **locally** on your machine.
*   If you have a GPU, ensure CUDA is enabled.
*   On CPU, it might take a few seconds to process.

**2. "Model not found" or Download errors?**
*   The first time you run "Magic Fridge", it will download model weights (~3GB). Please be patient.
*   Check your internet connection.

**3. Vector Store Error?**
*   If the bot says "No knowledge base available", you might need to rebuild the vector store.
*   Make sure the `Vector_Store_RAG` directory exists and contains data.

---

## 📄 License
This project is for educational purposes.
