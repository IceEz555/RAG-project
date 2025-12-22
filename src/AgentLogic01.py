from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.checkpoint.memory import InMemorySaver  
from langchain_core.runnables import RunnableConfig
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import ToolMessage
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
    - Always synthesize the information retrieved.
    """
)

# --------------------------------------------------------------------
# 1. MIDDLEWARE DEFINITIONS
# --------------------------------------------------------------------
import time

class SimpleLoggingMiddleware:
    """Middleware to log input and output to console for debugging."""
    def __init__(self):
        pass

    def on_request(self, inputs):
        if "messages" in inputs and inputs["messages"]:
            print(f"[{time.strftime('%X')}] 📥 User Input: {inputs['messages'][-1].content}")
        return inputs

    def on_response(self, outputs):
        if "messages" in outputs and outputs["messages"]:
            print(f"[{time.strftime('%X')}] 📤 Agent Output: {outputs['messages'][-1].content[:100]}...")
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

# --------------------------------------------------------------------
# 2. HELPER FUNCTIONS (AFTER MODEL)
# --------------------------------------------------------------------
def format_sources(raw_sources):
    """
    Clean and deduplicate sources from ToolMessages.
    """
    unique_sources = {}
    formatted_list = []
    
    # raw_sources in this context usually comes from ToolMessage content which might be a JSON string or text
    # But based on existing code, it seems to be the output of retrive_context tool
    
    for src in raw_sources:
        # Simple deduplication based on content string
        # In a real scenario, we might parse JSON if retrive_context returns structural data
        if src not in unique_sources:
            unique_sources[src] = True
            formatted_list.append(src)
            
    return formatted_list

# --------------------------------------------------------------------
# 3. ROUTING AGENT SETUP
# --------------------------------------------------------------------
from pydantic import BaseModel, Field

# General Agent (Chit-chat) - Now Stateful
general_model = init_chat_model("google_genai:gemini-2.5-flash-lite")

@tool
def general_tool(query: str):
    """A placeholder tool for the general agent if needed, or just rely on the LLM"""
    pass

general_system_prompt = "You are a friendly AI cooking assistant. Answer the following query casually, but politely decline if it's unrelated to food (unless it's a greeting)."

general_agent = create_agent(
    general_model,
    tools=[], # General agent might not need tools, or we can add dummy ones
    system_prompt=general_system_prompt,
    checkpointer=InMemorySaver()
)

# Router Definition
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: str = Field(
        ...,
        description="Given a user question choose to route it to 'cooking_agent' or 'general_agent'. "
                    "Use 'cooking_agent' for questions about food, recipes, ingredients, cooking methods, or kitchen tips. "
                    "Use 'general_agent' for greetings, chit-chat, or questions completely unrelated to cooking.",
    )

llm_router = init_chat_model("google_genai:gemini-2.5-flash-lite")
structured_llm_router = llm_router.with_structured_output(RouteQuery)

def route_question(query: str):
    try:
        result = structured_llm_router.invoke(query)
        return result.datasource
    except Exception as e:
        print(f"Routing Error: {e}")
        return "cooking_agent" # Fallback to cooking agent

# --------------------------------------------------------------------
# 4. COOKING AGENT (EXISTING RAG AGENT)
# --------------------------------------------------------------------
# Rename 'agent' to 'cooking_agent' for clarity
cooking_agent = create_agent(
    model,
    tools=[retrive_context],
    system_prompt=system_prompt,
    middleware=[
        SummarizationMiddleware(
            model="google_genai:gemini-2.5-flash-lite",
            trigger=("tokens", 4000),
            keep=("messages", 20)
        )
    ],
    checkpointer=InMemorySaver()
)

# --------------------------------------------------------------------
# 5. MAIN EXECUTION FUNCTION
# --------------------------------------------------------------------
# Create an instance of logging middleware
logger = SimpleLoggingMiddleware()

def get_answer(query: str, thread_id: str = "1") -> any:
    """Get final answer from the agent with Routing and Middleware."""
    
    # 1. Logging Input
    logger.on_request({"messages": [type('obj', (object,), {'content': query})]}) # Mock input object for simple logger
    
    # 2. Safety Check (Guardrail)
    if not safety_check(query):
        return "ขออภัยครับ ผมไม่สามารถตอบคำถามที่มีเนื้อหาไม่เหมาะสมหรืออันตรายได้ครับ ", []

    # 3. Routing
    destination = route_question(query)
    print(f"🔀 Routing to: {destination} (Thread ID: {thread_id})")

    response_text = ""
    sources = []
    
    # Config for the agent execution
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}} 
    final_messages = []

    target_agent = None
    
    if destination == "general_agent":
        target_agent = general_agent
    else: 
        target_agent = cooking_agent

    # Execute Selected Agent
    for event in target_agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
        stream_mode="values",
    ):
        final_messages = event["messages"]
            
    last_message = final_messages[-1]
    response_text = last_message.content
        
    # Extract sources from ToolMessages (mostly for cooking agent)
    for msg in final_messages:
        if isinstance(msg, ToolMessage):
            sources.append(msg.content)

    # 4. After Model (Format Sources)
    clean_sources = format_sources(sources)

    # 5. Logging Output
    logger.on_response({"messages": [type('obj', (object,), {'content': response_text})]})

    return response_text, clean_sources

