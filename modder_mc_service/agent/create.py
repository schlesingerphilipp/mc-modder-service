from langgraph.graph import END, START, StateGraph, MessagesState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from modder_mc_service.llms.agents import get_google_ai
from modder_mc_service.llms.tools_calling_invoke import invoke_with_tools
from modder_mc_service.util.llm_init import load_env,   LoadEnvResponse
from modder_mc_service.mcp.client import getClient
from modder_mc_service.tools.files import copy_folder
import os


async def create_mod_agent(mod_name: str, description: str = "Any") -> dict:
    """
    Endpoint to create a mod with a given name and description.
    """
    mcp_client = getClient()
    tools = await mcp_client.get_tools()
    tools += [copy_folder]
    callable_tools = {tool.name: tool for tool in tools}
    promt = "You are an Assistant that helps to create a mod for Minecraft. Your task is to copy a template folder to a new folder with the mod name"
    task = f"Copy the folder /mods/template to the folder /mods/{mod_name}"
    agent = get_google_ai(tools = tools)
    def chatbot(state: MessagesState) -> dict:
        return {"messages": invoke_with_tools(agent, callable_tools, state["messages"])}
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    graph = graph_builder.compile()
    
    state = {}
    state["messages"] = [
        SystemMessage(promt, origin_id="promt"), HumanMessage(task, origin_id="task_create")]
    graph.invoke(input=state)
    # check if the directory was created at ../mods/{mod_name}
    if not os.path.exists(f"/mods/{mod_name}"):
        raise Exception("Failed to create mod directory. Dir does not exist")
    # For demonstration, returning a simple dict
    return {"mod_name": mod_name, "description": description, "status": "created"}
