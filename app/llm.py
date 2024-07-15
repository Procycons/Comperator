import logging

import openai
from openai import chat
from openai.types.chat.chat_completion import ChatCompletion


logger = logging.getLogger(__name__)


class LLMModel:
    _instance = None

    def __init__(self, url: str, api_key: str, model_name: str) -> None:
        self.url = url
        self.api_key = api_key
        self.model_name = model_name

        
        self.openai_client = openai.OpenAI(
            base_url=url,
            api_key=api_key
        )
    
    def chat(self, prompt, sys_prompt="", max_token=1000, temp=0.) -> ChatCompletion | None:
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                max_tokens=max_token,
                temperature=temp,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt},
                ]
            )
        except Exception as e:
            logger.error("Error in creating campaigns from openAI:", str(e))
            return None
        return response

    def __new__(cls, url: str, api_key: str, model_name: str):
        if not cls._instance:
            cls._instance = super(LLMModel, cls).__new__(cls)
            cls._instance.__init__(url, api_key, model_name)
            
        return cls._instance
