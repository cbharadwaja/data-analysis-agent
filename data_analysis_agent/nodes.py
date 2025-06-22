import base64
import io
from typing import List

import pandas as pd
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from .state import AgentState
from .database import get_db_schema


class QuerySteps(BaseModel):
    steps: List[str] = Field(..., description="List of decomposed steps")


class UnderstandQueryNode:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "You break down analytical questions into smaller tasks."
                " Respond with JSON in the form {\"steps\": [..]}."
            )
        ),
        HumanMessage(content="{query}"),
    ])

    def __call__(self, state: AgentState) -> AgentState:
        try:
            messages = self.prompt.format_messages(query=state["original_query"])
            response = self.llm.invoke(messages)
            data = QuerySteps.model_validate_json(response.content)
            state["decomposed_queries"] = data.steps
        except Exception as e:  # pragma: no cover
            state["error_message"] = f"understand_query_node failed: {e}"
        return state


class GenerateSQLNode:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "You create SQLite queries to answer analytical questions."
                " Today's date is 2024-07-01. Use the following schema:\n{schema}"
            )
        ),
        HumanMessage(content="Task: {task}"),
    ])

    def __call__(self, state: AgentState) -> AgentState:
        try:
            task = state["decomposed_queries"][0]
            schema = get_db_schema()
            messages = self.prompt.format_messages(task=task, schema=schema)
            response = self.llm.invoke(messages)
            state["sql_query"] = (
                response.content.strip().split("```sql")[-1].split("```", 1)[0].strip()
            )
        except Exception as e:  # pragma: no cover
            state["error_message"] = f"generate_sql_node failed: {e}"
        return state


class ExecuteSQLNode:
    def __call__(self, state: AgentState) -> AgentState:
        import sqlite3

        try:
            conn = sqlite3.connect(get_db_schema.__globals__["DB_PATH"])
            df = pd.read_sql_query(state["sql_query"], conn)
            conn.close()
            state["dataframe_as_str"] = df.to_csv(index=False)
        except Exception as e:
            state["error_message"] = f"execute_sql_node failed: {e}"
        return state


class GenerateCodeNode:
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "You are a data scientist. Write Python code that analyzes the DataFrame df"
                " and produces a visualization using matplotlib or seaborn."
                " End with a print statement describing the chart."
            )
        ),
        HumanMessage(content="Original query: {query}\nData preview:\n{data}"),
    ])

    def __call__(self, state: AgentState) -> AgentState:
        try:
            df_head = (
                pd.read_csv(io.StringIO(state["dataframe_as_str"])).head().to_csv(index=False)
            )
            messages = self.prompt.format_messages(query=state["original_query"], data=df_head)
            response = self.llm.invoke(messages)
            state["visualization_code"] = (
                response.content.split("```python")[-1].split("```", 1)[0].strip()
            )
        except Exception as e:
            state["error_message"] = f"generate_code_node failed: {e}"
        return state


class ExecuteVizCodeNode:
    def __call__(self, state: AgentState) -> AgentState:
        img, desc = self.execute_python_code(
            state["visualization_code"], state["dataframe_as_str"]
        )
        if desc.startswith("execute_viz_code_node failed"):
            state["error_message"] = desc
        else:
            state["chart_image_b64"] = img
            state["chart_description"] = desc
        return state

    @staticmethod
    def execute_python_code(code: str, data: str) -> tuple[str, str]:
        df = pd.read_csv(io.StringIO(data))
        global_scope = {"pd": pd, "plt": plt, "df": df}
        buf = io.BytesIO()
        plt.clf()
        stdout = io.StringIO()
        import contextlib

        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, global_scope)  # pragma: no cover - dynamic execution
            plt.savefig(buf, format="png")
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode("utf-8")
            description = stdout.getvalue().strip()
            return img_b64, description
        except Exception as e:
            return "", f"execute_viz_code_node failed: {e}"


class ErrorHandlerNode:
    def __call__(self, state: AgentState) -> AgentState:
        print(state.get("error_message", "Unknown error"))
        return state

