from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent

# Load environment variables and initialize model and vector store
load_dotenv() # Load environment variables from .env file
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# Load existing vector store
vector_store = InMemoryVectorStore.load('Vector_store_original', embeddings)

# Define retrieval tool
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# Create agent with retrieval tool
tools = [retrieve_context]
# If desired, specify custom instructions
prompt = (
    "You are a helpful assistant. "
    "When you receive a response from a tool, you MUST summarize it and provide a final answer to the user. "
    "DO NOT return an empty response. "
    "Always synthesize the information retrieved."
)
agent = create_agent(model, tools, system_prompt=prompt)

# Function to get answer from agent
def getAnswer(query: str) -> any:
    """Get answer from agent."""
    final_answer = None
    for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",):
        print("This is inside get_answer - event:", event["messages"][-1].content)
    return event["messages"][-1].content