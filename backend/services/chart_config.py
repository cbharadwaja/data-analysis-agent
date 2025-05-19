import os
from openai_agents import Responses

class ChartConfigGenerator:
    def __init__(self, api_key: str, model: str):
        self.responses = Responses(api_key=api_key, model=model)

    def generate_many(self, nl_query: str, stats: dict) -> list:
        func = {
            'name': 'generateMultipleChartConfigs',
            'description': 'Produce Chart.js configs',
            'parameters': {
                'type': 'object',
                'properties': {
                    'configs': {'type': 'array', 'items': {
                        'type': 'object', 'properties': {
                            'type': {'type': 'string', 'enum': ['line','bar','pie']},
                            'xField': {'type': 'string'},
                            'yField': {'type': 'string'},
                            'title': {'type': 'string'}
                        }, 'required': ['type','xField','yField','title']
                    }}
                }, 'required': ['configs']
            }
        }
        prompt = (
            "Based on request and summary, decide charts.\n"
            f"Request: {nl_query}\nSummary: {stats}\nReturn via function call."
        )
        resp = self.responses.create(
            messages=[{'role': 'user', 'content': prompt}],
            functions=[func], function_call={'name':'generateMultipleChartConfigs'}
        )
        call = resp.choices[0].message.function_call
        data = {} if not call or not call.arguments else __import__('json').loads(call.arguments)
        return data.get('configs', [])