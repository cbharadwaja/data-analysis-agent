from typing import List, TypedDict

class AgentState(TypedDict, total=False):
    original_query: str
    decomposed_queries: List[str]
    sql_query: str
    dataframe_as_str: str
    visualization_code: str
    chart_image_b64: str
    chart_description: str
    error_message: str
