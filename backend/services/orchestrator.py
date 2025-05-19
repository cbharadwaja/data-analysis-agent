import os
from openai_agents import Agent, Tool
from services.data_loader import DataLoader
from services.nl2sql import NL2SQLTranslator
from services.sql_executor import SQLExecutor
from services.analyzer import DataAnalyzer
from services.insights_generator import InsightsGenerator
from services.chart_config import ChartConfigGenerator
from services.formatter import ResponseFormatter

API_KEY = os.getenv('OPENAI_API_KEY')
AGENT_MODEL = os.getenv('OPENAI_AGENT_MODEL','gpt-4o')
NL2SQL_MODEL = os.getenv('OPENAI_NL2SQL_MODEL','gpt-4')
INSIGHTS_MODEL = os.getenv('OPENAI_INSIGHTS_MODEL','gpt-4')
CHART_MODEL = os.getenv('OPENAI_CHART_MODEL','gpt-4')

# Tools
tools = [
    Tool('load_data', lambda c,f: DataLoader(c,f).load(), 'Load file'),
    Tool('describe_data', lambda df: DataAnalyzer(df).describe(), 'Describe'),
    Tool('nl_to_sql', lambda q: NL2SQLTranslator(API_KEY,NL2SQL_MODEL).translate(q), 'NL→SQL'),
    Tool('exec_sql', lambda sql: SQLExecutor().execute(sql), 'Execute SQL')
]
agent = Agent(name='DataAgent', description='Orchestrate...', tools=tools, llm={'model_name':AGENT_MODEL})

class AgentOrchestrator:
    def __init__(self):
        self.agent = agent; self.agent.api_key = API_KEY
        self.insight = InsightsGenerator(API_KEY, INSIGHTS_MODEL)
        self.charter = ChartConfigGenerator(API_KEY, CHART_MODEL)

    def analyze_nl(self, nl_query):
        df = self.agent.run('exec_sql', self.agent.run('nl_to_sql', nl_query))
        stats = DataAnalyzer(df).describe()
        table = DataAnalyzer(df).to_records()
        insights = self.insight.generate(stats, nl_query)
        configs = self.charter.generate_many(nl_query, stats)
        charts = [{**cfg, 'chartData': {'labels':df[cfg['xField']].tolist(), 'datasets':[{'label':cfg['yField'],'data':df[cfg['yField']].tolist(),'fill':False}]}} for cfg in configs]
        return ResponseFormatter().format(stats, insights, charts, table)

    def analyze_file(self, content, filename, nl_query):
        df = DataLoader(content, filename).load()
        stats = DataAnalyzer(df).describe()
        table = DataAnalyzer(df).to_records()
        insights = self.insight.generate(stats, nl_query)
        configs = self.charter.generate_many(nl_query, stats)
        charts = [{**cfg, 'chartData': {'labels':df[cfg['xField']].tolist(), 'datasets':[{'label':cfg['yField'],'data':df[cfg['yField']].tolist(),'fill':False}]}} for cfg in configs]
        return ResponseFormatter().format(stats, insights, charts, table)