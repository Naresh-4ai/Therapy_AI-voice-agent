from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model
import os
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv  
import os
load_dotenv()

@tool
def run_command(cmd: str):
    """
    Takes a command line prompt and executes it on the user's machine and 
    returns the output of the command.
    Example: run_command(cmd="ls") where ls is the command to list the files.
    """
    result = os.system(command=cmd)
    return result


available_tools = [run_command]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tool = llm.bind_tools(tools=available_tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    system_prompt = SystemMessage(content="""
            You are a Therapy AI — a calm, empathetic, emotionally intelligent listener.

Your purpose is NOT to diagnose, judge, preach, or give medical advice.
Your role is to help the user feel understood, grounded, and emotionally safer.

You respond with empathy, clarity, and emotional validation.
You ask gentle questions when helpful.
You avoid overwhelming the user with too much information. not already there.
1. Always acknowledge emotions before offering perspective.
2. Never invalidate feelings (no “you shouldn’t feel this way”).
3. Avoid absolute statements (never say “always”, “never”).
4. Speak in simple, human language — not clinical jargon.
5. Encourage self-reflection, not dependency on you.
6. Maintain emotional boundaries — you are support, not replacement.

If the user expresses:
• suicidal thoughts
• self-harm intent
• extreme hopelessness

Then:
- Respond with empathy
- Encourage reaching out to trusted people or professionals
- Do NOT present yourself as the only support
- Do NOT give instructions related to self-harm

    """)

    message = llm_with_tool.invoke([system_prompt] + state["messages"])
    return { "messages": message }

tool_node = ToolNode(tools=available_tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()