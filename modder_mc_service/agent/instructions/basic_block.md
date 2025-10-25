## Adding a basic custom block without attributes
This adds a block with a custom skin. The block does not possess any specific properties.
We refer to the new block as myblock
- add src/generated/resources/assets/examplemod/blockstates/myblock.json
```json
    {
  "variants": {
    "": {
      "model": "tutorialmod:block/myblock"
    }
  }
}
```
- add src/generated/resources/assets/examplemod/models/block/myblock.json
```json
{
  "parent": "minecraft:block/cube_all",
  "textures": {
    "all": "tutorialmod:block/myblock"
  }
}
```
- add src/generated/resources/assets/examplemod/models/item/myblock.json
```json
{
  "parent": "tutorialmod:block/myblock"
}
```
- in src/main/resources/assets/examplemod/lang/en_us.json
    - Add a line `"block.tutorialmod.myblock": "Block of MyBlock",` at the top.
- add src/main/resources/assets/examplemod/textures/block/myblock.png with an image of choice
- in src/main/java/com/example/examplemod/block/ModBlocks.java add lines:
```java
       public static final RegistryObject<Block> MY_BLOCK = registerBlock("myblock",
                (properties) -> new Block(properties
                        .strength(4f).requiresCorrectToolForDrops()));
```
