import os
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing Anthropic library for Claude API
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    logger.warning("Anthropic library not found. API mode will be unavailable.")
    ANTHROPIC_AVAILABLE = False

# Try importing libraries for local model
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    LOCAL_MODEL_AVAILABLE = torch.cuda.is_available()  # Check if GPU is available
except ImportError:
    logger.warning("Transformers/torch libraries not found. Local model will be unavailable.")
    LOCAL_MODEL_AVAILABLE = False

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

class ClaudeService:
    def __init__(self, api_key: Optional[str] = None, local_model_path: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.api_key = api_key
        self.client = None
        self.local_model = None
        self.local_tokenizer = None
        self.local_model_path = local_model_path
        self.model_loaded = False

    def init_api_client(self, api_key: Optional[str] = None) -> bool:
        """Initialize the Claude API client with the provided API key"""
        if not ANTHROPIC_AVAILABLE:
            logger.error("Anthropic library not installed. Cannot use API mode.")
            return False

        try:
            key_to_use = api_key if api_key else self.api_key
            if not key_to_use:
                logger.error("No API key provided.")
                return False
                
            self.api_key = key_to_use
            self.client = anthropic.Anthropic(api_key=key_to_use)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Claude API client: {e}")
            return False

    def load_local_model(self) -> bool:
        """Load a local model for offline use"""
        if not LOCAL_MODEL_AVAILABLE:
            logger.error("Required libraries missing or GPU unavailable. Cannot load local model.")
            return False
            
        try:
            logger.info(f"Loading local model from {self.local_model_path}")
            self.local_tokenizer = AutoTokenizer.from_pretrained(self.local_model_path)
            
            # Use lower precision for efficiency
            self.local_model = AutoModelForCausalLM.from_pretrained(
                self.local_model_path, 
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            self.model_loaded = True
            logger.info("Local model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            return False
            
    def generate_response_api(self, messages: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
        """Generate a response using Claude API"""
        if not self.client:
            if not self.init_api_client():
                return "Error: Claude API client not initialized. Please check your API key.", {}
        
        try:
            # Convert messages to Claude's expected format
            formatted_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    formatted_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    formatted_messages.append({"role": "assistant", "content": msg["content"]})
                elif msg["role"] == "system":
                    formatted_messages.append({"role": "system", "content": msg["content"]})

            # Make API request to Claude
            start_time = time.time()
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=formatted_messages
            )
            elapsed = time.time() - start_time
            
            metadata = {
                "model": "claude-3-sonnet-20240229",
                "latency": round(elapsed, 2),
                "source": "api",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
            return response.content[0].text, metadata
            
        except Exception as e:
            logger.error(f"Error generating response from Claude API: {e}")
            return f"Error communicating with Claude: {str(e)}", {"error": str(e)}
    
    def generate_response_local(self, messages: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
        """Generate a response using a local model"""
        if not self.model_loaded and not self.load_local_model():
            return "Error: Local model could not be loaded.", {}
            
        try:
            # Format messages into a conversation the model can understand
            conversation = ""
            for msg in messages:
                if msg["role"] == "system":
                    # Include system message at the beginning
                    conversation += f"<|system|>\n{msg['content']}\n"
                elif msg["role"] == "user":
                    conversation += f"<|user|>\n{msg['content']}\n"
                elif msg["role"] == "assistant":
                    conversation += f"<|assistant|>\n{msg['content']}\n"
            
            # Add the final assistant prompt
            conversation += "<|assistant|>\n"
            
            # Generate response
            start_time = time.time()
            inputs = self.local_tokenizer(conversation, return_tensors="pt")
            
            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {key: value.to('cuda') for key, value in inputs.items()}
            
            # Generate without gradient calculation to save memory
            with torch.no_grad():
                outputs = self.local_model.generate(
                    **inputs,
                    max_new_tokens=500,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.95
                )
                
            response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the assistant's response from the generated text
            response = response.split("<|assistant|>\n")[-1].strip()
            
            elapsed = time.time() - start_time
            
            metadata = {
                "model": self.local_model_path,
                "latency": round(elapsed, 2),
                "source": "local"
            }
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Error generating response from local model: {e}")
            return f"Error generating response locally: {str(e)}", {"error": str(e)}
    
    def generate_response(self, messages: List[Dict[str, str]], use_local: bool = False) -> Tuple[str, Dict[str, Any]]:
        """Generate a response using either Claude API or local model"""
        if use_local:
            return self.generate_response_local(messages)
        else:
            return self.generate_response_api(messages)

# Initialize service singleton
claude_service = ClaudeService()
