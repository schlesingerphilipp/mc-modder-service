# Minecraft Mod Generation Service
A Service to generate Mods on natural language specifications. 
The user can verbally describe what they want to add/modify in the game of Minecraft. 
The argentic System will generate the required resources, pack them to a jar and deliver it to the mods folder of the User. The user can reload or open a create world, where this mod is enabled, and inspect the changes. 

![Architecture diagram](mc-modder-flow.drawio.png)

_High-level flow: user request → agent → mod resources → packaged mod (jar)_
