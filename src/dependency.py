import os
import time
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field
from token_counter import TokenCounter

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

# Initialize models
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
general_model = init_chat_model("google_genai:gemini-2.5-flash-lite")

# Initialize embeddings and vector store
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Load existing vector store
# Note: Assuming relative path consistency relative to execution or use absolute path
try:
    vector_store = InMemoryVectorStore.load('../Vector_Store_RAG', embeddings)
except Exception as e:
    print(f"Warning: Could not load vector store: {e}")
    vector_store = None

# --------------------------------------------------------------------
# TOOLS
# --------------------------------------------------------------------
@tool(response_format="content_and_artifact")
def retrive_context(query: str):
    """Retrieve information to help answer a query."""
    if vector_store is None:
        return "No knowledge base available.", []
        
    retrieved_docs = vector_store.similarity_search(query, k=4) 
    serialized = "\n\n".join(f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrieved_docs)
    return serialized, retrieved_docs

@tool
def general_tool(query: str):
    """A placeholder tool for the general agent if needed, or just rely on the LLM"""
    pass

# --------------------------------------------------------------------
# HELPER FUNCTIONS & MIDDLEWARE
# --------------------------------------------------------------------
class SimpleLoggingMiddleware:
    """Middleware to log input and output to console for debugging with token counting."""
    def __init__(self, token_counter=None):
        self.token_counter = token_counter

    def on_request(self, inputs):
        if "messages" in inputs and inputs["messages"]:
            user_input = inputs['messages'][-1].content
            print(f"[{time.strftime('%X')}] 📥 User Input: {user_input}")
            
            if self.token_counter:
                input_tokens = self.token_counter.add_input(user_input)
                print(f"[{time.strftime('%X')}] 🔢 Input Tokens: {input_tokens}")
        return inputs

    def on_response(self, outputs):
        if "messages" in outputs and outputs["messages"]:
            agent_output = outputs['messages'][-1].content
            print(f"[{time.strftime('%X')}] 📤 Agent Output: {agent_output[:100]}...")
            
            if self.token_counter:
                output_tokens = self.token_counter.add_output(agent_output)
                print(f"[{time.strftime('%X')}] 🔢 Output Tokens: {output_tokens}")
                stats = self.token_counter.get_stats()
                print(f"[{time.strftime('%X')}] 📊 Total Session: {stats['total_tokens']} tokens (Input: {stats['input_tokens']}, Output: {stats['output_tokens']})")
        return outputs

def safety_check(text: str) -> bool:
    """
    Simple Guardrail: Check for dangerous keywords.
    Returns True if SAFE, False if UNSAFE.
    """
    # คำต้องห้าม (ตัวอย่าง)
    DANGEROUS_KEYWORDS = ["bomb", "suicide", "poison", "ระเบิด", "ยาพิษ"]
    for word in DANGEROUS_KEYWORDS:
        if word in text.lower():
            return False
    return True

def format_sources(raw_sources):
    """
    Clean and deduplicate sources from ToolMessages.
    """
    unique_sources = {}
    formatted_list = []
    
    for src in raw_sources:
        if src not in unique_sources:
            unique_sources[src] = True
            formatted_list.append(src)
            
    return formatted_list
