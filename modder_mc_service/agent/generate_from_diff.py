import os
from langgraph.graph import END, START, StateGraph
from modder_mc_service.llms.agents import get_google_ai
from modder_mc_service.agent.nodes import CapabilityExtractor, CapabilityDiffExecutor, State, STEP_FINISHED
from modder_mc_service.tools.files import FakeMCPClient
from dotenv import load_dotenv
from langsmith import traceable

# TODO: on module load will not work with real MCP
tools = FakeMCPClient().get_tools()

@traceable
def execute_capability(state: State, capability: dict, mods_folder: str = "/mods") -> State:
    capability_executor_node = CapabilityDiffExecutor(
        name=f"capability_executor_diff_{capability['title']}",
        model=get_google_ai(),
        tools=tools,
        capability=capability,
        mod_name=state["mod_name"],
        mod_domain=state["mod_domain"],
        mods_folder=mods_folder,
    )
    state["messages"] = []
    state = capability_executor_node.call(state)
    while not state[STEP_FINISHED]:
        # It might executes multiple functions like reading/writing files until the step is finished.
        # TODO: set limits?
        state = capability_executor_node.call(state)
    return state

@traceable
def plan_and_execute_capability_steps(state: State) -> State: #TODO: why is it dict not state?
    """
    Execute all capability steps for the given capabilities in the state.

    Args:
        state: Current state of the mod generation.
    Returns:
        state: Current state of the mod generation after all capability executions.
    """
    for capability in state["capabilities"]["capabilities"]:
            state = execute_capability(state, capability)
            # TODO: What to do with the state after each capability execution?
            # We would verify etc now. For now we just proceed to the next capability.
    return state

@traceable
def _generate_code_from_diff(promt: str, mod_name: str, mod_id: str, mod_domain: str) -> dict:
    """
    Second iteration of the mod generation, where we use the git diff to represent 
    the changes needed to be done to the mod codebase for each capability.
    Further we employ the middleware 'todolist' to guide the agent.
    """
    capability_extractor_node = CapabilityExtractor(
        name="capability_extractor",
        model=get_google_ai(), # TODO: Try SLMs from Docker
    )
    
    graph_builder = StateGraph(State)
    graph_builder.add_node(capability_extractor_node.name, capability_extractor_node.func)
    graph_builder.add_node("plan_and_execute_steps", plan_and_execute_capability_steps)
    graph_builder.add_edge(START, capability_extractor_node.name)
    graph_builder.add_edge(capability_extractor_node.name, "plan_and_execute_steps")
    graph_builder.add_edge("plan_and_execute_steps", END)
    graph = graph_builder.compile()
    state = State(
        mod_id=mod_id,
        mod_name=mod_name,
        mod_domain=mod_domain,
        messages=[],
        capabilities={},
        step_finished=False,
        last_error=None,
        raw_input=promt,
    )
    graph.invoke(input=state)
    return {"mod_name": mod_name, "status": "better look yourself :D. We are debugging here"}

async def generate_code_from_diff(promt: str, mod_name: str, mod_id: str, mod_domain: str) -> dict:
    return _generate_code_from_diff(promt, mod_name, mod_id, mod_domain)