LangGraph Data Analysis Agent: System Architecture
This document outlines the architecture of the Data Analysis Agent, a system designed to interpret natural language queries, perform data analysis, and generate visualizations. The agent is built using the LangGraph framework and powered by OpenAI models.

1. Core Philosophy
The agent follows a synchronous, sequential pipeline where a user's query is progressively transformed into a final visual answer. Each step is handled by a specialized "agent" or "node" within a stateful graph. The central idea is to break down a complex data analysis task into a series of manageable, automated steps, from understanding intent to generating code and executing it.

2. High-Level Flow
The system operates as a state machine orchestrated by LangGraph. The state is passed from one node to the next, with each node adding its output to the state object.

graph TD
    A[User Query] --> B(Agent 1: Understand & Decompose);
    B --> C(Agent 2: Generate SQL);
    C --> D(Execute SQL & Fetch Data);
    D --> E(Agent 3&4: Generate Python Code);
    E --> F(Agent 5: Execute Code & Generate Chart);
    F --> G[Final Output: Chart + Description];

    subgraph Error Handling
        B -- on error --> H{Error};
        C -- on error --> H;
        D -- on error --> H;
        E -- on error --> H;
        F -- on error --> H;
    end

    H --> I[End with Error Message];

3. System Components
3.1. Environment & Configuration
Dependencies: The system relies on key Python libraries: langgraph, langchain-openai, pandas, matplotlib, seaborn, and python-dotenv.

API Key Management: The OpenAI API key is managed securely using a .env file and loaded into the environment at runtime, preventing hard-coding of credentials.

3.2. Database
Type: A self-contained SQLite database (sales_data.db) is used for this implementation. This makes the agent portable and easy to run without external database setup.

Schema: A simple sales table is created with columns relevant to sales analysis (product_name, region, sale_date, quantity, price_per_unit).

Interaction:

A helper function get_db_schema() provides the table schema to the SQL Generation agent, which is critical for context.

Data is fetched using pandas.read_sql_query() after a SQL query is generated.

3.3. LangGraph State (AgentState)
This is the central nervous system of the agent. It's a TypedDict that carries information through the graph. Each node reads from and writes to this shared state.

Key Fields:

original_query: The initial user input.

decomposed_queries: A list of sub-tasks from the first agent.

sql_query: The generated SQL to fetch data.

dataframe_as_str: The fetched data, serialized as a CSV string.

visualization_code: The generated Python code for analysis and plotting.

chart_image_b64: The final chart, encoded as a Base64 string.

chart_description: A text summary of the chart's insight.

error_message: A field to capture and pass on any errors.

3.4. The Agent Nodes
The core logic resides in a series of nodes, each corresponding to an agent's responsibility.

Agent 1: understand_query_node

Model: gpt-4o (with structured output).

Input: original_query.

Responsibility: Decomposes the high-level user query into a list of specific, actionable sub-queries. Using structured output (Pydantic) ensures the response is a clean, usable list.

Output: decomposed_queries.

Agent 2: generate_sql_node

Model: gpt-4o.

Input: The first decomposed_queries and the database schema.

Responsibility: Translates the primary analytical task into a valid SQLite query. The prompt includes the schema and a hard-coded "current date" to correctly interpret time-based queries (e.g., "last quarter").

Output: sql_query.

Node: execute_sql_node

Responsibility: This is not an LLM-based agent but a functional tool. It connects to the database, executes the sql_query, fetches the result into a pandas DataFrame, and serializes it into a CSV string.

Output: dataframe_as_str.

Agent 3 & 4 (Combined): generate_code_node

Model: gpt-4.

Input: original_query, decomposed_queries, and the head of the dataframe_as_str.

Responsibility: This is a powerful, combined node that acts as a data scientist. It generates a single Python script that:

Performs data analysis on the provided DataFrame (df).

Uses matplotlib or seaborn to create a plot.

Uses a print() statement to output a textual description of the plot.

Output: visualization_code.

Agent 5: execute_viz_code_node

Responsibility: Executes the visualization_code using the execute_python_code tool. This is the "display" agent.

Output: chart_image_b64 and chart_description.

3.5. Code Execution Tool (execute_python_code)
This is a critical, and sensitive, component.

Functionality: It takes the generated Python code and the data string. It uses Python's exec() function to run the code in a controlled scope that has pandas, matplotlib, etc., pre-imported.

Output Capturing: It captures the matplotlib plot into an in-memory buffer and encodes it to Base64. It also captures any text sent to standard output (via print()) to use as the chart description.

Security: The implementation explicitly warns that exec() is not secure for production. A real-world deployment would require a sandboxed environment (e.g., Docker, WebAssembly) to mitigate the risk of arbitrary code execution.

4. Graph Structure and Control Flow
Compilation: The nodes are assembled into a StateGraph and compiled into a runnable application (app).

Entry Point: The graph starts at the understand_query_node.

Error Handling: The architecture uses conditional edges. After each primary step, the should_continue function (which is implicitly handled by the graph's transition logic) would check for an error_message in the state. If an error is present, the flow is redirected to a handle_error_node, which prints the error and terminates the process. This makes the agent resilient to failures in any of the steps.