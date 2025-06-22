from langgraph.graph import StateGraph

from .state import AgentState
from .database import init_db
from .nodes import (
    UnderstandQueryNode,
    GenerateSQLNode,
    ExecuteSQLNode,
    GenerateCodeNode,
    ExecuteVizCodeNode,
    ErrorHandlerNode,
)


class DataAnalysisAgent:
    def __init__(self) -> None:
        init_db()
        self.graph = StateGraph(AgentState)
        self._add_nodes()
        self._add_edges()
        self.graph.set_entry_point("understand_query")
        self.app = self.graph.compile()

    def _add_nodes(self) -> None:
        self.graph.add_node("understand_query", UnderstandQueryNode())
        self.graph.add_node("generate_sql", GenerateSQLNode())
        self.graph.add_node("execute_sql", ExecuteSQLNode())
        self.graph.add_node("generate_code", GenerateCodeNode())
        self.graph.add_node("execute_viz_code", ExecuteVizCodeNode())
        self.graph.add_node("handle_error", ErrorHandlerNode())

    def _add_edges(self) -> None:
        self.graph.add_edge("understand_query", "generate_sql")
        self.graph.add_edge("generate_sql", "execute_sql")
        self.graph.add_edge("execute_sql", "generate_code")
        self.graph.add_edge("generate_code", "execute_viz_code")

        self.graph.add_conditional_edges("understand_query", self._ok, {True: "generate_sql", False: "handle_error"})
        self.graph.add_conditional_edges("generate_sql", self._ok, {True: "execute_sql", False: "handle_error"})
        self.graph.add_conditional_edges("execute_sql", self._ok, {True: "generate_code", False: "handle_error"})
        self.graph.add_conditional_edges("generate_code", self._ok, {True: "execute_viz_code", False: "handle_error"})
        self.graph.add_conditional_edges("execute_viz_code", self._ok, {True: None, False: "handle_error"})

    @staticmethod
    def _ok(state: AgentState) -> bool:
        return "error_message" not in state

    def run(self, query: str) -> AgentState:
        state: AgentState = {"original_query": query}
        return self.app.invoke(state)

