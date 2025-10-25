from modder_mc_service.agent.create import create_mod_agent
from modder_mc_service.agent.block import create_basic_block
import asyncio

if __name__ == "__main__":
    #asyncio.run(create_mod_agent("example_mod"))
    promt = ""
    mod_name = "example_mod"
    asyncio.run(create_basic_block(promt=promt, mod_name=mod_name))