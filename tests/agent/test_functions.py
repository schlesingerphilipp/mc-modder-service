from langchain.messages import ToolMessage, AIMessage
import os
import json

def assert_that_step_made_dirs(state, expected_folder_path: str):
    ai_message = state["messages"][-2] # get the AI message before the tool response
    tool_call_name, tool_call_args = _get_func_name_and_args_from_ai_message(ai_message)
    assert tool_call_name == "make_dirs", f"Expected tool 'make_dirs', got '{tool_call_name}'"
    actual_path: str = tool_call_args.get("path", None)
    assert actual_path is not None, "No path argument found in tool call"
    actual_path = actual_path.rstrip("/")
    assert actual_path == expected_folder_path, f"Expected folder path {expected_folder_path}, got {actual_path}"

def assert_that_step_overwrote_file(state, expected_file_path: str, expected_content: str):
    ai_message = state["messages"][-2] # get the AI message before the tool response
    tool_call_name, tool_call_args = _get_func_name_and_args_from_ai_message(ai_message)
    assert tool_call_name == "overwrite_file", f"Expected tool 'overwrite_file', got '{tool_call_name}'"
    actual_path = tool_call_args.get("path", None)
    assert actual_path is not None, "No path argument found in tool call"
    assert actual_path == expected_file_path, f"Expected file path {expected_file_path}, got {actual_path}"
    assert os.path.exists(expected_file_path), f"Expected file {expected_file_path} to exist"
    with open(expected_file_path, "r") as f:
        actual_content = f.read().strip()
    actual_content = actual_content.replace(" ", "")
    expected_content = expected_content.replace(" ", "")
    assert actual_content == expected_content

def assert_that_step_inserted_to_file(state, expected_file_path: str, inserted_content: str):
    ai_message = state["messages"][-2] # get the AI message before the tool response
    tool_call_name, tool_call_args = _get_func_name_and_args_from_ai_message(ai_message)
    assert tool_call_name == "overwrite_file", f"Expected tool 'overwrite_file', got '{tool_call_name}'"
    actual_path = tool_call_args.get("path", None)
    assert actual_path is not None, "No path argument found in tool call"
    assert actual_path == expected_file_path, f"Expected file path {expected_file_path}, got {actual_path}"
    assert os.path.exists(expected_file_path), f"Expected file {expected_file_path} to exist"
    with open(expected_file_path, "r") as f:
        actual_content = f.read().strip()
    actual_content = actual_content.replace(" ", "")
    inserted_content = inserted_content.replace(" ", "")
    assert inserted_content in actual_content, f"Expected inserted content not found in file {expected_file_path}"

def assert_that_step_read_the_file(state, expected_file_path: str):
    ai_message = state["messages"][-2] # get the AI message before the tool response
    tool_call_name, tool_call_args = _get_func_name_and_args_from_ai_message(ai_message)
    assert tool_call_name == "read_file", f"Expected tool 'read_file', got '{tool_call_name}'"
    actual_path = tool_call_args.get("path", None)
    assert actual_path is not None, "No path argument found in tool call"
    assert actual_path == expected_file_path, f"Expected file path {expected_file_path}, got {actual_path}"

def _get_func_name_and_args_from_ai_message(message: AIMessage):
    assert isinstance(message, AIMessage), "Message is not an AIMessage"
    func = message.additional_kwargs.get("function_call", None)
    assert func is not None, "No function call found in AI message"
    func_name = func.get("name", None)
    assert func_name is not None, "No function name found in function call"
    func_args = func.get("arguments", None)
    assert func_args is not None, "No function arguments found in function call"
    func_args_dict = json.loads(func_args)
    return func_name, func_args_dict