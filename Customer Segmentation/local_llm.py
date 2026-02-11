import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace

# Global variable to cache the model to avoid reloading
_cached_model = None

def load_local_chat_model(model_name="Qwen/Qwen2.5-7B-Instruct"):
    """
    Loads a local LLM and returns a LangChain ChatModel interface.
    Uses 4-bit quantization for efficiency.
    """
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    print(f"🔄 Loading local model: {model_name} ...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load model with 4-bit quantization and CPU offload support
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
            load_in_4bit=True, 
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            llm_int8_enable_fp32_cpu_offload=True, # Enable CPU offloading
            trust_remote_code=True
        )

        # Create a text-generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            return_full_text=False
        )

        # Wrap in LangChain interfaces
        llm = HuggingFacePipeline(pipeline=pipe)
        
        # ChatHuggingFace automatically handles the chat template of the model
        chat_model = ChatHuggingFace(llm=llm, tokenizer=tokenizer)
        
        print("✅ Local model loaded successfully!")
        _cached_model = chat_model
        return chat_model
        
    except Exception as e:
        print(f"❌ Error loading local model: {e}")
        print("Tip: Make sure you have installed: pip install torch transformers accelerate bitsandbytes langchain-huggingface")
        raise e
