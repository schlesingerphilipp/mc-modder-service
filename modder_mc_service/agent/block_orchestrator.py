from modder_mc_service.tools.files import read_file_contents
mod_name = "example_mod"
block_instructions = read_file_contents("modder_mc_service/agent/instructions/create_basic_block.md")
system_msg_basic = f"You are an Assistant that helps to create a mod for Minecraft. Your task is to create a basic Block by creating and editing files in /mods/{mod_name}. There are instructions on how to create the basic block below: \n {block_instructions} \n You can find assests like png images in /assets folder."