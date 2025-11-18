from modder_mc_service.agent.nodes import CapabilityStepExecutor, CapabilityItem, STEP_FINISHED
from modder_mc_service.tools.files import read_file_contents
from modder_mc_service.llms.agents import get_google_ai
from modder_mc_service.tools.files import FakeMCPClient
from tests.agent.test_functions import assert_that_step_made_dirs, assert_that_step_overwrote_file, assert_that_step_inserted_to_file, assert_that_step_read_the_file
from tests.agent.data_capability_test import get_expected_basic_block_for_step, ELEMENT_NAME, MOD_NAME, MOD_ID, MOD_DOMAIN
import os
import shutil
import pytest
from dotenv import load_dotenv

@pytest.fixture  
def temp_dir(tmp_path):  
    return tmp_path  

tools = FakeMCPClient().get_tools()

def test_get_instructions():
    basic_block_instructions_folder = "modder_mc_service/agent/instructions/block_basic"
    element_name = "test_block"
    mod_name = "examplemod"
    mod_id = "examplemod"
    mod_domain = "com/example"
    mods_folder = "/mods"
    base_instruction = "Bla Bla $MOD_NAME Bla $CAPABILITY_STEP Bla $CAPABILITY_INSTRUCTION Bla $MOD_ID Bla $ELEMENT_NAME Bla $MOD_DOMAIN Bla $MODS_FOLDER Bla"
    instruction = CapabilityStepExecutor.get_instructions(
        instruction=base_instruction,
        title="Basic Block",
        element_name=element_name,
        mod_domain=mod_domain,
        mod_name=mod_name,
        mod_id=mod_id,
        capability_folder=basic_block_instructions_folder,
        index=1,
        mods_folder=mods_folder,
    )
    expected_instruction = '''Bla Bla examplemod Bla Basic Block Bla create the directory /mods/examplemod/src/generated/resources/assets/examplemod/blockstates/
add the file /mods/examplemod/src/generated/resources/assets/examplemod/blockstates/test_block.json
with the content:
```json
{
    "variants": {
        "": {
        "model": "examplemod:block/test_block"
        }
    }
}
``` Bla examplemod Bla test_block Bla com/example Bla /mods Bla'''
    # compare line by line to avoid issues with whitespace
    instruction_lines = instruction.strip().splitlines()
    expected_lines = expected_instruction.strip().splitlines()
    assert len(instruction_lines) == len(expected_lines)
    for instr_line, expected_line in zip(instruction_lines, expected_lines):
        assert instr_line.strip() == expected_line.strip(), f"Line mismatch:\nExpected: {expected_line}\nGot: {instr_line}"




def test_capability_step_basic_block(tmpdir):
    load_dotenv(dotenv_path=".env", override=True)
    basic_block_instructions_folder = "modder_mc_service/agent/instructions/block_basic"
    # setup copy /mods/template to tmpdir/mod_name
    shutil.copytree("/mods/template", os.path.join(tmpdir, MOD_NAME))
    capability = CapabilityItem(title="sdf", folder=basic_block_instructions_folder, elementName=ELEMENT_NAME).model_dump()
    model = get_google_ai() # doenloading local model atm. TODO: replace with local
    mod_meta = {
        "mod_name": MOD_NAME,
        "mod_id": MOD_ID,
        "mod_domain": MOD_DOMAIN,
    }
    # Files in the capability folder
    steps = 6
    for step_index in range(1, steps +1):
        initial_state = {
        "mod_name": MOD_NAME,
        "mod_id": MOD_ID,
        "mod_domain": MOD_DOMAIN,
        "messages": [],
        STEP_FINISHED: False,
        }
        expected_folder_path, expected_file_path, expected_content, inserted_content = get_expected_basic_block_for_step(step_index)
        expected_folder_path_step_i = f"{str(tmpdir)}/{expected_folder_path}" if expected_folder_path else None
        expected_file_path_step_i = f"{str(tmpdir)}/{expected_file_path}" if expected_file_path else None
        assert_step(
            model=model,
            tools=tools,
            state=initial_state,
            capability=capability,
            mod_meta=mod_meta,
            tmpdir=tmpdir,
            expected_folder_path=expected_folder_path_step_i,
            expected_file_path=expected_file_path_step_i,
            expected_content=expected_content,
            inserted_content =inserted_content,
            index=step_index,
        )
    print("done")

    

def assert_step(model, tools, state, capability, mod_meta, tmpdir, expected_folder_path, expected_file_path, expected_content, inserted_content, index):
    mod_name = mod_meta["mod_name"]
    mod_id = mod_meta["mod_id"]
    mod_domain = mod_meta["mod_domain"]
    node = CapabilityStepExecutor("name", model, tools, capability, index, mod_name, mod_id, mod_domain, str(tmpdir))
    state = node.call(state)
    if expected_folder_path:
        # some steps create folders, some don't
        assert_that_step_made_dirs(state, expected_folder_path)
    state = node.call(state)
    if expected_content:
        # overwriting file with content
        assert_that_step_overwrote_file(state, expected_file_path, expected_content)
    if inserted_content:
        # first reading the file
        assert_that_step_read_the_file(state, expected_file_path)
        # then overwriting 
        state = node.call(state)
        assert_that_step_inserted_to_file(state, expected_file_path, inserted_content)
