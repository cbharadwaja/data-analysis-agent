from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

UNDERSTAND_QUERY_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessage(
        content=(
            "You break down analytical questions into smaller tasks." \
            " Respond with JSON in the form {\"steps\": [..]}."
        )
    ),
    HumanMessage(content="{query}"),
])

GENERATE_SQL_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessage(
        content=(
            "You create SQLite queries to answer analytical questions." \
            " Today's date is 2024-07-01. Use the following schema:\n{schema}"
        )
    ),
    HumanMessage(content="Task: {task}"),
])

GENERATE_CODE_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessage(
        content=(
            "You are a data scientist. Write Python code that analyzes the DataFrame df" \
            " and produces a visualization using matplotlib or seaborn." \
            " End with a print statement describing the chart."
        )
    ),
    HumanMessage(content="Original query: {query}\nData preview:\n{data}"),
])

__all__ = [
    "UNDERSTAND_QUERY_PROMPT",
    "GENERATE_SQL_PROMPT",
    "GENERATE_CODE_PROMPT",
]
