# Import from variables.py and dependency.py
from variables import system_prompt, general_system_prompt
from dependency import (
    model, 
    general_model, 
    retrive_context, 
    general_tool, 
    SimpleLoggingMiddleware, 
    safety_check, 
    format_sources,
    init_chat_model,
    create_agent,
    SummarizationMiddleware,
    RunnableConfig,
    InMemorySaver,
    ToolMessage,
    BaseModel,
    Field
)

# --------------------------------------------------------------------
# AGENT SETUP
# --------------------------------------------------------------------

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
        return "cooking_agent" # Fallback

# General Agent (Stateful)
general_agent = create_agent(
    general_model,
    tools=[], 
    system_prompt=general_system_prompt,
    checkpointer=InMemorySaver()
)

# Cooking Agent (Stateful)
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
# MAIN EXECUTION FUNCTION
# --------------------------------------------------------------------
logger = SimpleLoggingMiddleware()

def get_answer(query: str, thread_id: str = "1") -> any:
    """Get final answer from the agent with Routing and Middleware."""
    
    # 1. Logging Input
    logger.on_request({"messages": [type('obj', (object,), {'content': query})]}) 
    
    # 2. Safety Check
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
    try:
        for event in target_agent.stream(
            {"messages": [{"role": "user", "content": query}]},
            config=config,
            stream_mode="values",
        ):
            final_messages = event["messages"]
            
        if final_messages:
            last_message = final_messages[-1]
            response_text = last_message.content
            
            # Extract sources from ToolMessages
            for msg in final_messages:
                if isinstance(msg, ToolMessage):
                    sources.append(msg.content)
        else:
            response_text = "Sorry, I couldn't generate a response."

    except Exception as e:
        response_text = f"An error occurred during execution: {e}"
        print(response_text)

    # 4. After Model (Format Sources)
    clean_sources = format_sources(sources)

    # 5. Logging Output
    logger.on_response({"messages": [type('obj', (object,), {'content': response_text})]})

    return response_text, clean_sources
