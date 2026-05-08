import os
from models import get_llm
from dotenv import load_dotenv
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from fastapi import FastAPI
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
import uvicorn
from nodes import grade_documents, generate_query_or_respond, generate_answer, rewrite_question
from tools import retrieve_documents

load_dotenv()

 
def build_agent():
    """Build the agent's graph."""
    graph = StateGraph(MessagesState)

    graph.add_node(generate_query_or_respond)
    graph.add_node("retrieve", ToolNode([retrieve_documents]))
    graph.add_node(rewrite_question)
    graph.add_node(generate_answer)

    graph.add_edge(START, "generate_query_or_respond")

    
    graph.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )
    graph.add_conditional_edges(
        "retrieve",
        grade_documents,
    )

    graph.add_edge("generate_answer", END)
    graph.add_edge("rewrite_question", "generate_query_or_respond")
    graph = graph.compile(
      checkpointer=MemorySaver()
     )
    return graph


app = FastAPI()

add_langgraph_fastapi_endpoint(
  app=app,
  agent=LangGraphAGUIAgent(
    name="sample_agent",
    description="An example agent to use as a starting point for your own agent.",
    graph=build_agent(),
  ),
  path="/",
)

def main():
  """Run the uvicorn server."""
  uvicorn.run(
    "agent:app",
    host="0.0.0.0",
    port=8123,
    reload=True,
  )

if __name__ == "__main__":
  main()