import os
from langgraph.graph import END, START, StateGraph
from modder_mc_service.llms.agents import get_google_ai
from modder_mc_service.agent.nodes import CapabilityExtractor, CapabilityStepExecutor, State, STEP_FINISHED
from modder_mc_service.tools.files import FakeMCPClient

# TODO: on module load will not work with real MCP
tools = FakeMCPClient().get_tools()

def count_files_in_folder(folder_path: str) -> list:
    """
    Count the number of files in a folder.
    Args:
        folder_path: Path to the folder.
    Returns:
        Number of files in the folder.
    """
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        file_count += len(files)
    return file_count

def execute_capability_step(state: State, capability: dict, index: int) -> State:
    capability_executor_node = CapabilityStepExecutor(
        name=f"capability_executor_{index}",
        model=get_google_ai(),
        tools=tools,
        capability=capability,
        capability_index=index+1,
        mod_name=state["mod_name"],
        mod_id=state["mod_id"],
        mod_domain=state["mod_domain"],
    )
    state["messages"] = []
    state = capability_executor_node.call(state)
    while not state[STEP_FINISHED]:
        # It might executes multiple functions like reading/writing files until the step is finished.
        # TODO: set limits?
        state = capability_executor_node.call(state)
    return state

def plan_and_execute_capability_steps(state: State) -> State: #TODO: why is it dict not state?
    """
    Gets the List of capabilities and executes them one by one with the CapabilityStepExecutor Node.

    Args:
        mod_name: Name of the mod.
        description: Description of the mod.
        capabilities: Capabilities required for the mod.
    Returns:
        A dictionary with the results of the execution.
    """
    for capability in state["capabilities"]["capabilities"]:
        files_in_folder = count_files_in_folder(capability["folder"])
        for index in range(files_in_folder):
            state = execute_capability_step(state, capability, index)
            # TODO: What to do with the state after each capability execution?
            # We would verify etc now. For now we just proceed to the next capability.
    return state


async def generate_code(promt: str, mod_name: str, mod_id: str, mod_domain: str) -> dict:
    """
    A first iteration of how the code generation could work.
    We expect that the mod folder was copied from the template folder.
    Some elements like validation and error handling are missing at this point in time.
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
