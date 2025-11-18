import shutil
import os
from tests.agent.data_capability_test import ELEMENT_NAME, MOD_NAME, MOD_ID, MOD_DOMAIN, EXPECTED 
from modder_mc_service.agent.nodes import CapabilityItem, STEP_FINISHED
from modder_mc_service.agent.generate_from_diff import execute_capability
from dotenv import load_dotenv

def test_capability_diff_basic_block(tmpdir):
    load_dotenv(dotenv_path=".env", override=True)
    basic_block_instructions_folder = "modder_mc_service/agent/diffs/block_basic.txt"
    # setup copy /mods/template to tmpdir/mod_name
    mod_folder = os.path.join(tmpdir, MOD_NAME)
    shutil.copytree("/mods/template", mod_folder)
    capability = CapabilityItem(title="sdf", folder=basic_block_instructions_folder, elementName=ELEMENT_NAME).model_dump()
    initial_state = {
        "mod_name": MOD_NAME,
        "mod_id": MOD_ID,
        "mod_domain": MOD_DOMAIN,
        "messages": [],
        STEP_FINISHED: False,
    }
    execute_capability(initial_state, capability, mods_folder=str(tmpdir))
    # Assert final expected files here
    for expected_tuple in EXPECTED:
        (folder_path, file_path, file_content, inserted_content) = expected_tuple
        if folder_path is not None:
            full_folder_path = os.path.join(tmpdir, folder_path)
            assert os.path.exists(full_folder_path), f"Expected folder path does not exist: {full_folder_path}"
        if file_path is not None:
            full_file_path = os.path.join(tmpdir, file_path)
            assert os.path.exists(full_file_path), f"Expected file path does not exist: {full_file_path}"
        if file_content is not None:
            with open(full_file_path, "r") as f:
                actual_content = f.read().replace(" ", "").replace("\n", "")
                expected_content_cleaned = file_content.replace(" ", "").replace("\n", "")
                assert actual_content == expected_content_cleaned, f"File content does not match for {full_file_path}"
        if inserted_content is not None:
            with open(full_file_path, "r") as f:
                actual_content = f.read().replace(" ", "").replace("\n", "")
                expected_inserted_cleaned = inserted_content.replace(" ", "").replace("\n", "")
                assert expected_inserted_cleaned in actual_content, f"Inserted content not found in {full_file_path}"