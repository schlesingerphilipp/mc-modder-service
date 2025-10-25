from modder_mc_service.agent.create import create_mod_agent
from modder_mc_service.agent.block import generate_code
import asyncio

if __name__ == "__main__":
    #asyncio.run(create_mod_agent("example_mod"))
    promt = "Plaase create a basic block with a black texture."
    mod_name = "example_mod"
    mod_id = "example_mod"
    asyncio.run(generate_code(promt=promt, mod_name=mod_name, mod_id=mod_id))