from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
import bs4
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, PyPDFDirectoryLoader
from dotenv import load_dotenv
import os
from langchain.tools import tool
from langchain.agents import create_agent

# Load environment variables and initialize model and vector store
load_dotenv() # Load environment variables from .env file
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Load existing vector store
vector_store = InMemoryVectorStore.load('../Vector_Store_RAG', embeddings)

# Tool for retrieving context
@tool(response_format="content_and_artifact")
def retrive_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=4 ) #ใช้ similarity search หา top-2 documents
    serialized = "\n\n".join(f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrieved_docs)
    return serialized, retrieved_docs

# System prompt
system_prompt =("""
    - You are a helpful AI assistant.
    - When you receive a response from a tool, you MUST summarize it and provide a final answer to the user.
    - DO NOT return an empty response.
    - Always synthesize the information retrieved."""
)
agent = create_agent(model,tools=[retrive_context], system_prompt=system_prompt)

def get_answer(query: str) -> str:
    """Get final answer from the agent"""
    final_answer = None
    for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",):
        print("This is inside get_answer - event:", event["messages"][-1].content)
    return event["messages"][-1].content
