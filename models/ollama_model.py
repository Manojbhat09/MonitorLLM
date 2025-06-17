import requests
import json
import os
import logging
from dotenv import load_dotenv
from config.logger_setup import setup_logging
from utils.sanitizer import remove_code_block

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

class OllamaModel:
    def __init__(self, model_name="llama3.1", host="http://localhost:11434"):
        logger.debug("Initializing OllamaModel...")
        load_dotenv()
        self.model_name = model_name
        self.host = host
        self.base_url = f"{host}/api"
        logger.debug(f"OllamaModel initialized with model: {model_name}, host: {host}")

    def _make_request(self, endpoint, data):
        """Makes a request to the Ollama API."""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Ollama: {e}")
            return None

    def _generate_completion(self, messages, system_prompt=None):
        """Generates a completion using Ollama chat API."""
        try:
            # Convert messages to Ollama format
            ollama_messages = []
            
            if system_prompt:
                ollama_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            for msg in messages:
                if msg["role"] in ["user", "assistant", "system"]:
                    ollama_messages.append(msg)
            
            data = {
                "model": self.model_name,
                "messages": ollama_messages,
                "stream": False
            }
            
            response = self._make_request("chat", data)
            if response and "message" in response:
                return response["message"]["content"].strip()
            return None
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return None

    def validate_command(self, command):
        """Validates the command to ensure it is safe and valid to execute."""
        logger.debug(f"Validating command: {command}")
        
        system_prompt = ("You are a senior system administrator who must validate shell commands if there are any errors or not and return the proper/fixed version. "
                        "Also if the input contains anything other than a pure command (e.g., comments, flags, etc.), you must remove them. "
                        "If the command is already correct, you must return it as is. If the command is in a code block, you must remove the code block. "
                        "Use simple commands and avoid using complex commands for fewer errors. "
                        "Anticipate the user's needs and provide the best possible solution.")
        
        messages = [
            {"role": "user", "content": "ls -d */"},
            {"role": "assistant", "content": "ls -d */"},
            {"role": "user", "content": "```sh\ndocker system df | awk '/VOLUME/{getline; while($1 ~ /^[[:alnum:]]/){print $2, $3, $4;s+=($3~/GB/?$2*1024:($3~/kB/?$2/1024:$2));getline}} END{print \"Total Size: \" s\"MB\"}' | sort -k1,1rn\n```"},
            {"role": "assistant", "content": "sudo docker volume ls -q | xargs -I {} docker volume inspect {} --format='{{ .Name }}{{ printf \"\\t\" }}{{ .Mountpoint }}' | sudo awk '{ system(\"sudo du -hs \" $2) }' | sort -rh"},
            {"role": "user", "content": command}
        ]
        
        validated_command = self._generate_completion(messages, system_prompt)
        if validated_command:
            output = remove_code_block(validated_command)
            logger.debug(f"Validated command: {output}")
            return output
        
        logger.warning("Failed to validate command.")
        return None

    def get_command_suggestion(self, context, prompt):
        """Generates shell commands based on the provided context and prompt."""
        logger.debug(f"Generating command suggestion for context: {context} and prompt: {prompt}")
        
        system_prompt = ("You are a helpful assistant that must only output shell commands and nothing else. "
                        "Anticipate the user's needs and provide the best possible solution. "
                        "Do not include any comments or flags in the output.")
        
        messages = [
            {"role": "user", "content": context},
            {"role": "user", "content": prompt}
        ]
        
        suggested_command = self._generate_completion(messages, system_prompt)
        if suggested_command:
            logger.debug(f"Suggested command before validation: {suggested_command}")
            suggested_command = self.validate_command(suggested_command)
            logger.debug(f"Suggested command after validation: {suggested_command}")
            return suggested_command
        
        logger.warning("Failed to generate command suggestion.")
        return None

    def answer_question(self, context, question):
        """Generates answers to questions based on the provided context and question."""
        logger.debug(f"Answering question for context: {context} and question: {question}")
        
        system_prompt = "You are a knowledgeable assistant who provides detailed answers to questions."
        
        messages = [
            {"role": "user", "content": context},
            {"role": "user", "content": question}
        ]
        
        answer = self._generate_completion(messages, system_prompt)
        if answer:
            logger.debug(f"Answer: {answer}")
            return answer
        
        logger.warning("Failed to generate answer.")
        return None

    def chat_with_context(self, context, message, file_contents=None):
        """Enhanced chat function with file context support."""
        logger.debug(f"Chat with context: {message}")
        
        system_prompt = ("You are a helpful AI assistant with access to terminal context and file contents. "
                        "Provide detailed, contextual responses based on the terminal activity and any referenced files. "
                        "If the user references files with @filename, use the provided file contents in your response.")
        
        messages = []
        
        # Add terminal context
        if context:
            messages.append({"role": "user", "content": f"Terminal context:\n{context}"})
        
        # Add file contents if provided
        if file_contents:
            for filename, content in file_contents.items():
                messages.append({"role": "user", "content": f"File {filename} contents:\n{content}"})
        
        # Add the main message
        messages.append({"role": "user", "content": message})
        
        response = self._generate_completion(messages, system_prompt)
        if response:
            logger.debug(f"Chat response: {response}")
            return response
        
        logger.warning("Failed to generate chat response.")
        return "Sorry, I couldn't generate a response at this time." 