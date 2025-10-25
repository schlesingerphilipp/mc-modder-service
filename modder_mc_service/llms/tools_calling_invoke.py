from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from typing import List

def invoke_with_tools(model: BaseChatModel, tools: dict, messages: List[BaseMessage]) -> AIMessage:
    response: AIMessage = model.invoke(input=messages)
    if len(response.content) > 0:
        messages.append(response)
    elif response.tool_calls:
        for tool_call in response.tool_calls:
            selected_tool = tools[tool_call["name"].lower()]
            try:
                tool_msg = selected_tool.invoke(tool_call)
                # only add the response if the tool call is successful
                messages.append(response)
                messages.append(tool_msg)
            except ValueError as e:
                raise e
    return messages

def recursive_invoke_with_tools(model: BaseChatModel, tools: dict, messages: List[BaseMessage]) -> AIMessage:
    """Just a test, how far an agent gets left on its own.

    Args:
        model (BaseChatModel): _description_
        tools (dict): _description_
        messages (List[BaseMessage]): _description_

    Raises:
        e: _description_

    Returns:
        AIMessage: _description_
    """
    response: AIMessage = model.invoke(input=messages)
    if len(response.content) > 0:
        return [response]
    elif response.tool_calls:
        for tool_call in response.tool_calls:
            selected_tool = tools[tool_call["name"].lower()]
            messages.append(response)
            try:
                tool_msg = selected_tool.invoke(tool_call)
                # only add the response if the tool call is successful
                messages.append(tool_msg)
                recursive_invoke_with_tools(model, tools, messages)
            except Exception as e:
                messages.append(HumanMessage(content=f"Tool {tool_call['name']} failed with error: {str(e)}"))
    return messages