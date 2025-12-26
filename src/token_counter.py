import time
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# --------------------------------------------------------------------
# TOKEN COUNTING & TRACKING (Google Genai Client)
# --------------------------------------------------------------------
class TokenCounter:
    """Track token usage for input and output using Google Genai Client API."""
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.session_history = []
        self.model_name = model_name
        
        # Initialize Google Genai Client for token counting
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            self.client = genai.Client(api_key=api_key)
            print(f"✅ TokenCounter initialized with Google Genai Client ({model_name})")
        except Exception as e:
            print(f"Warning: Could not initialize Google Genai Client: {e}")
            self.client = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string using Google Genai Client API."""
        if self.client is None:
            # Fallback: rough approximation (1 token ≈ 4 characters)
            return len(text) // 4
        
        try:
            # Use Google Genai Client's count_tokens method
            result = self.client.models.count_tokens(
                model=self.model_name,
                contents=text
            )
            return result.total_tokens
        except Exception as e:
            print(f"Error counting tokens with Google Genai Client: {e}")
            # Fallback to character-based approximation
            return len(text) // 4
    
    def add_input(self, text: str):
        """Add input text and count tokens."""
        tokens = self.count_tokens(text)
        self.total_input_tokens += tokens
        self.session_history.append({
            "type": "input",
            "text": text[:100],  # Store first 100 chars
            "tokens": tokens,
            "timestamp": time.strftime('%X')
        })
        return tokens
    
    def add_output(self, text: str):
        """Add output text and count tokens."""
        tokens = self.count_tokens(text)
        self.total_output_tokens += tokens
        self.session_history.append({
            "type": "output",
            "text": text[:100],  # Store first 100 chars
            "tokens": tokens,
            "timestamp": time.strftime('%X')
        })
        return tokens
    
    def get_total_tokens(self):
        """Get total tokens (input + output)."""
        return self.total_input_tokens + self.total_output_tokens
    
    def get_stats(self):
        """Get detailed statistics."""
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.get_total_tokens(),
            "session_count": len(self.session_history),
            "model": self.model_name
        }
    
    def reset(self):
        """Reset all counters."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.session_history = []
