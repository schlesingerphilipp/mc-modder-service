from typing import Callable, List, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables.base import Runnable
from pydantic import BaseModel, Field
from modder_mc_service.tools.files import make_dirs, copy_folder, read_file_contents, read_file_contents_tool, list_dir_contents, overwrite_file, copy_file

STEP_FINISHED = "step_finished"

class CapabilityItem(BaseModel):
    """
    A single capability item.
    """

    title: str
    folder: str
    elementName: str
class Capabilities(BaseModel):
    """
    Selected capabilities, which will satisfy the user's request.
    """

    capabilities: List[CapabilityItem]



class State(TypedDict):
    """
    A custom State for our LangGraph. We want to control the graph flow with the field 'translation_finished'.
    We do this, so the Model can freely call functions and do chains of thoughts, until it is done.

    Args:
        TypedDict (_type_): _description_
    """
    raw_input: str
    mod_id: str
    mod_name: str
    mod_domain: str
    messages: Annotated[list, add_messages]
    capabilities: dict
    current_capability: str
    step_finished: bool
    last_error: str



class GraphNode:
    """A genral Class, just holding the minimal information any Node in a LangGraph requires."""

    func: Callable
    name: str

    def __init__(self, func: Callable, name: str):
        self.func = func
        self.name = name


class CapabilityExtractor(GraphNode):
    """
    The Agent to extract the Capabilities.
    """

    model: BaseChatModel
    INSTRUCTIONNS_EXTRACTOR = f"""
        You are an Assistant that helps to create a mod for Minecraft.
        This assistance program has certain capabilities like adding basic blocks or giving blocks sound effects. 
        Depending on the user's request,
        Your task is to think about what elements (like Blocks, Items, Sound Effects, Textures, etc.) are required to satisfy the user's request,
        and for each of these elements extract the fitting capabilities from a list of capabilities.
        Each capability has a title a folder where its instructions are stored, and an elementName which corresponds to the name of
        the element in the source code. So if you add a block, which should be black, the elementName could be 'black_block'.
        
        These capabilities are:
        {read_file_contents("modder_mc_service/agent/instructions/capabilities.md")}
        """

    def __init__(self, name, model: BaseChatModel):
        self.model = model.with_structured_output(Capabilities)
        super().__init__(func=self.call, name=name)

    def call(self, state: State):
        """
        A single call to the CapabilityExtractor.
        The flow control of the conversation happens in the Graph.

        Args:
            state (State): The current state of the Conversation.

        Returns:
            _type_: The State after the Configurator was invoked once.
        """
        messages = [
            SystemMessage(
                content=self.INSTRUCTIONNS_EXTRACTOR
            ),
            HumanMessage(content=state["raw_input"]),
        ]
        response: Capabilities = self.model.invoke(input=messages)
        # Validating? How?
        state["capabilities"] = response.model_dump()
        return state


class CapabilityStepExecutor(GraphNode):
    """
    An Agent to perform a Capability Step. 
    Afterwards its results get verified.
    """

    model: BaseChatModel
    instruction = """
        You are an Assistant that helps to create a mod for Minecraft.
        This assistance program has certain capabilities like adding basic blocks or giving blocks sound effects.
        Each capability has m,ultiple steps to perform. You will be given one of these steps to perform.
        The step corresponds to a capability, which is executed for one element of the mod.
        Elements of the mod can be Blocks, Items, Sound Effects, Textures, etc.
        The name of this element is $ELEMENT_NAME.
        The MOD_ID is $MOD_ID.
        The MOD_NAME is $MOD_NAME.

        Your task is to perform the following capability step: $CAPABILITY_STEP
        This is the instruction for this capability:
        $CAPABILITY_INSTRUCTION
        You can create and edit files in /$MODS_FOLDER/$MOD_NAME (absolute path). 
        You can find assets like png images and soundfiles ogg in /assets folder (absolute path).
        Use the available tools to perform the step.
        When you are done with the step, respond with 'STEP FINISHED'.
        """

    def __init__(self, name, model: BaseChatModel, tools: List[Runnable], capability: dict, capability_index: int, mod_name: str, mod_id: str, mod_domain: str, mods_folder: str = "/mods"):
        self.model = model.bind_tools(tools=tools)
        self.tools = {tool.name: tool for tool in tools}
        self.capability_instruction = CapabilityStepExecutor.get_instructions(
            instruction=self.instruction,
            title=capability["title"],
            element_name=capability["elementName"],
            mod_domain=mod_domain,
            mod_name=mod_name,
            mod_id=mod_id,
            capability_folder=capability["folder"],
            index=capability_index,
            mods_folder=mods_folder,
        )
        super().__init__(self.call, name=name)

    @staticmethod
    def get_instructions(instruction, title, element_name, mod_domain, mod_name, mod_id, capability_folder, index, mods_folder) -> str:
        capability_instruction = read_file_contents(f"{capability_folder}/{index}.md")
        instruction = instruction.replace("$CAPABILITY_STEP", title
            ).replace("$CAPABILITY_INSTRUCTION", capability_instruction
            ).replace("$MOD_ID", mod_id
            ).replace("$ELEMENT_NAME", element_name
            ).replace("$MOD_DOMAIN", mod_domain
            ).replace("$MODS_FOLDER", mods_folder
            ).replace("$MOD_NAME", mod_name)
        return instruction
    def call(self, state: State):
        """
        A single call to the Agent.
        The flow control of the conversation happens in the Graph.
        The Transator will decide if it should call functions, or directly reply.

        Args:
            state (State): The current state of the Conversation.

        Returns:
            _type_: The State after the Agent was invoked once, and maybe one new function call results.
        """
        messages = state["messages"]
        if not messages or len(messages) == 0:

            messages = [
                SystemMessage(content=self.capability_instruction),
                HumanMessage(content="Perform the capability step as described above."),
            ]
        response: AIMessage = self.model.invoke(input=messages)
        if len(response.content) > 0:
            messages.append(response)
            # The Agent outputs something to the user, so this step is finished.
            # TODO: Better detection if step is finished. Use langgraph edges with state condition.
            state[STEP_FINISHED] = True
        elif response.tool_calls:
            for tool_call in response.tool_calls:
                selected_tool = self.tools[tool_call["name"].lower()]
                try:
                    tool_msg = selected_tool.invoke(tool_call)
                    # only add the response if the tool call is successful
                    messages.append(response)
                    messages.append(tool_msg)
                except ValueError as e:
                    state[STEP_FINISHED] = True
                    state["last_error"] = str(e)
        state["messages"] = messages
        return state