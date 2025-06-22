import base64
import logging
from dotenv import load_dotenv

from data_analysis_agent.graph import DataAnalysisAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)


def run(query: str):
    agent = DataAnalysisAgent()
    return agent.run(query)


if __name__ == "__main__":
    result = run(input("Enter your analysis question: "))
    if result.get("chart_image_b64"):
        with open("chart.png", "wb") as f:
            f.write(base64.b64decode(result["chart_image_b64"]))
        print("Chart saved to chart.png")
    if result.get("chart_description"):
        print("\nDescription:\n", result["chart_description"])
    if result.get("error_message"):
        print("\nError:\n", result["error_message"])

