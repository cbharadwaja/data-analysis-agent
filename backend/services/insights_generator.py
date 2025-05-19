import os
from openai_agents import Responses

class InsightsGenerator:
    def __init__(self, api_key: str, model: str):
        self.responses = Responses(api_key=api_key, model=model)

    def generate(self, stats: dict, nl_query: str) -> str:
        prompt = (
            "You are a data insights assistant. Based on the summary and request,"
            f" provide concise insights.\nRequest: {nl_query}\nSummary: {stats}\nInsights:"
        )
        resp = self.responses.create(
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=150
        )
        return resp.choices[0].message.content.strip()