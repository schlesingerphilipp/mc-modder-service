from langgraph.graph import END, START, StateGraph, MessagesState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from modder_mc_service.llms.agents import get_google_ai
from modder_mc_service.llms.tools_calling_invoke import recursive_invoke_with_tools
from modder_mc_service.util.llm_init import load_env,   LoadEnvResponse
from modder_mc_service.mcp.client import getClient
from modder_mc_service.tools.files import make_dirs, copy_folder, read_file_contents, read_file_contents_tool, list_dir_contents, overwrite_file, copy_file
import os


async def create_basic_block(promt: str, mod_name: str) -> dict:
    """
    Create a Basic Block using the provided prompt.
    """
    mcp_client = getClient()
    tools = await mcp_client.get_tools()
    tools += [make_dirs, copy_folder, copy_file, read_file_contents_tool, list_dir_contents, overwrite_file]
    callable_tools = {tool.name: tool for tool in tools}
    instructions = read_file_contents("modder_mc_service/agent/instructions/basic_block.md")
    promt = f"You are an Assistant that helps to create a mod for Minecraft. Your task is to create a basic Block by creating and editing files in /mods/{mod_name} (absolute path). There are instructions on how to create the basic block below: \n {instructions} \n You can find assests like png images in /assets folder (absolute path)."
    agent = get_google_ai(tools = tools)
    def chatbot(state: MessagesState) -> dict:
        return {"messages": recursive_invoke_with_tools(agent, callable_tools, state["messages"])}
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    graph = graph_builder.compile()
    
    state = {}
    state["messages"] = [
        SystemMessage(promt, origin_id="promt"), HumanMessage(promt, origin_id="task_create")]
    graph.invoke(input=state)
    # check if the directory was created at ../mods/{mod_name}
    if not os.path.exists(f"/mods/{mod_name}"):
        raise Exception("Failed to create mod directory. Dir does not exist")
    # For demonstration, returning a simple dict
    return {"mod_name": mod_name, "description": description, "status": "created"}
