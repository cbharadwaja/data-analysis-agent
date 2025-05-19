import os
from openai_agents import Responses

class NL2SQLTranslator:
    def __init__(self, api_key: str, model: str):
        self.responses = Responses(api_key=api_key, model=model)

    def translate(self, nl_query: str) -> str:
        prompt = (
            "Convert this natural language request into a valid SQL SELECT on 'raw_data':\n"
            f"{nl_query}\nSQL:"
        )
        resp = self.responses.create(
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()