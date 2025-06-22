import base64
import io
import logging
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .prompts import (
    GENERATE_CODE_PROMPT,
    GENERATE_SQL_PROMPT,
    UNDERSTAND_QUERY_PROMPT,
)
from .state import AgentState
from .database import get_db_schema


class QuerySteps(BaseModel):
    steps: List[str] = Field(..., description="List of decomposed steps")


logger = logging.getLogger(__name__)


class UnderstandQueryNode:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = UNDERSTAND_QUERY_PROMPT

    def __call__(self, state: AgentState) -> AgentState:
        try:
            logger.info("Understanding query: %s", state.get("original_query"))
            messages = self.prompt.format_messages(query=state["original_query"])
            response = self.llm.invoke(messages)
            data = QuerySteps.model_validate_json(response.content)
            state["decomposed_queries"] = data.steps
        except Exception as e:  # pragma: no cover
            logger.error("understand_query_node failed: %s", e)
            state["error_message"] = f"understand_query_node failed: {e}"
        return state


class GenerateSQLNode:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = GENERATE_SQL_PROMPT

    def __call__(self, state: AgentState) -> AgentState:
        try:
            logger.info("Generating SQL for task: %s", state["decomposed_queries"][0])
            task = state["decomposed_queries"][0]
            schema = get_db_schema()
            messages = self.prompt.format_messages(task=task, schema=schema)
            response = self.llm.invoke(messages)
            state["sql_query"] = (
                response.content.strip().split("```sql")[-1].split("```", 1)[0].strip()
            )
        except Exception as e:  # pragma: no cover
            logger.error("generate_sql_node failed: %s", e)
            state["error_message"] = f"generate_sql_node failed: {e}"
        return state


class ExecuteSQLNode:
    def __call__(self, state: AgentState) -> AgentState:
        import sqlite3

        try:
            logger.info("Executing SQL query")
            conn = sqlite3.connect(get_db_schema.__globals__["DB_PATH"])
            df = pd.read_sql_query(state["sql_query"], conn)
            conn.close()
            state["dataframe_as_str"] = df.to_csv(index=False)
        except Exception as e:
            logger.error("execute_sql_node failed: %s", e)
            state["error_message"] = f"execute_sql_node failed: {e}"
        return state


class GenerateCodeNode:
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    prompt = GENERATE_CODE_PROMPT

    def __call__(self, state: AgentState) -> AgentState:
        try:
            logger.info("Generating visualization code")
            df_head = (
                pd.read_csv(io.StringIO(state["dataframe_as_str"])).head().to_csv(index=False)
            )
            messages = self.prompt.format_messages(query=state["original_query"], data=df_head)
            response = self.llm.invoke(messages)
            state["visualization_code"] = (
                response.content.split("```python")[-1].split("```", 1)[0].strip()
            )
        except Exception as e:
            logger.error("generate_code_node failed: %s", e)
            state["error_message"] = f"generate_code_node failed: {e}"
        return state


class ExecuteVizCodeNode:
    def __call__(self, state: AgentState) -> AgentState:
        logger.info("Executing visualization code")
        img, desc = self.execute_python_code(
            state["visualization_code"], state["dataframe_as_str"]
        )
        if desc.startswith("execute_viz_code_node failed"):
            logger.error(desc)
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
            logger.error("execute_viz_code_node failed: %s", e)
            return "", f"execute_viz_code_node failed: {e}"


class ErrorHandlerNode:
    def __call__(self, state: AgentState) -> AgentState:
        logger.error(state.get("error_message", "Unknown error"))
        return state

