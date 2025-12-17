# Smart Budget Chef (Cooking Guru) - Project Plan

A "Smart Budget Chef" chatbot (Cooking Guru) that recommends recipes based on available ingredients and budget, utilizing RAG (Retrieval-Augmented Generation) for recipe sourcing and mock data for pricing.

## 🎯 Objectives
1.  **Smart Recommendations:** Suggest 1-3 recipes based on user inquiry.
2.  **Budget Awareness:** Calculate approximate cost of ingredients.
3.  **Local Context:** Support Thai language and local ingredient pricing.
4.  **Data Driven:** Use PDF/Web recipe data and JSON-based price lists.

## 🛠 Tech Stack
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Chat Interface, Sidebar controls |
| **Backend** | Python 3.12 | Core logic |
| **LLM** | Gemini 2.5 Flash Lite | Reasoning & Generation |
| **Orchestration** | LangChain | RAG implementation (Embeddings, Chains) |
| **Vector DB** | ChromaDB / InMemory | Storing recipe embeddings |
| **Data Source (Recipes)** | PDF + Web | `Booklet.pdf` & `kohplanner.com` |
| **Data Source (Prices)** | JSON | `data/market_prices.json` (Mock DB) |

## 🏗 Architecture
1.  **Data Ingestion Layer:**
    *   Loaders: `PyPDFLoader`, `WebBaseLoader`
    *   Processing: `RecursiveCharacterTextSplitter`
    *   Store: `InMemoryVectorStore` (with caching)
2.  **Retrieval Layer:**
    *   Embeddings: `models/embedding-001`
    *   Search: Similarity Search (k=3-4)
3.  **Reasoning Layer (Agent):**
    *   System Prompt: "Smart Budget Chef" persona (Thai language).
    *   Chain: `create_retrieval_chain` combines retrieval + generation.
4.  **Application Layer:**
    *   Streamlit App (`cooking_bot.py`) for user interaction.

## 🗓 Development Plan & Status

### Phase 1: Preparation (✅ Completed)
- [x] Define Project Structure
- [x] Create Mock Price Database (`market_prices.json`)
- [x] Initial Streamlit Layout (`cooking_bot.py`)

### Phase 2: Core Logic (🔄 In Progress)
- [x] **RAG Implementation:**
    - [x] PDF Loader (`Booklet.pdf`)
    - [x] Web Loader (`kohplanner.com` - *Fixed/Tested*)
    - [x] Vector Store Setup (`RAG-Test.ipynb`)
    - [x] System Prompt Engineering
- [x] **Price Calculation:**
    - [x] Mock Price Logic (`chef_service.py`)
- [ ] **Agent Integration:**
    - [ ] Port logic from Notebook to `src/chef_service.py`
    - [ ] Connect Agent to Streamlit UI

### Phase 3: Frontend & Final Polish (TODO)
- [ ] Update Streamlit UI to use real Agent
- [ ] Add Sidebar for Budget/Health constraints
- [ ] Display formatted Recipe Cards
- [ ] Testing & Validation modules

## 📂 Project Structure
```text
RAG-project/
├── data/
│   ├── market_prices.json      # Mock Price DB
│   └── recipes/
│       └── Booklet.pdf         # Recipe Data
├── src/
│   ├── chef_service.py         # Backend Logic (Agent)
│   └── cooking_bot.py          # Frontend (Streamlit)
├── RAG-Test/                   # Prototyping Area
│   └── RAG-Test.ipynb          # Verified RAG Notebook
├── requirements.txt
└── Project_Plan.md             # This file
```
