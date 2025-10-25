# Notes about different Modding Actions
Each sections documents what needs to be done, to achieve a certain goal

## Adding a basic custom block without attributes
This adds a block with a custom skin. The block does not possess any specific properties.
We refer to the new block as myblock
- add src/generated/resources/assets/tutorialmod/blockstates/myblock.json
```json
    {
  "variants": {
    "": {
      "model": "tutorialmod:block/myblock"
    }
  }
}
```
- add src/generated/resources/assets/tutorialmod/models/block/myblock.json
```json
{
  "parent": "minecraft:block/cube_all",
  "textures": {
    "all": "tutorialmod:block/myblock"
  }
}
```
- add src/generated/resources/assets/tutorialmod/models/item/myblock.json
```json
{
  "parent": "tutorialmod:block/myblock"
}
```
- in src/main/resources/assets/tutorialmod/lang/en_us.json
    - Add a line `"block.tutorialmod.myblock": "Block of MyBlock",` at the top.
- add src/main/resources/assets/tutorialmod/textures/block/myblock.png with an image of choice
- in src/main/java/net/kaupenjoe/tutorialmod/block/ModBlocks.java add lines:
```java
       public static final RegistryObject<Block> MY_BLOCK = registerBlock("myblock",
                (properties) -> new Block(properties
                        .strength(4f).requiresCorrectToolForDrops()));
```

### Giving the Block a Sound Effect
- Add in src/main/java/net/kaupenjoe/tutorialmod/sound/ModSounds.java Line:
```java
    public static final RegistryObject<SoundEvent> MYBLOCK_BREAK = registerSoundEvent("myblock_break");
    public static final RegistryObject<SoundEvent> MYBLOCK_STEP = registerSoundEvent("myblock_step");
    public static final RegistryObject<SoundEvent> MYBLOCK_PLACE = registerSoundEvent("myblock_place");
    public static final RegistryObject<SoundEvent> MYBLOCK_HIT = registerSoundEvent("myblock_hit");
    public static final RegistryObject<SoundEvent> MYBLOCK_FALL = registerSoundEvent("myblock_fall");

  
public static final ForgeSoundType MYBLOCK_SOUNDS = new ForgeSoundType(1f, 1f,
            ModSounds.MYBLOCK_BREAK, ModSounds.MYBLOCK_STEP, ModSounds.MYBLOCK_PLACE,
            ModSounds.MYBLOCK_HIT, ModSounds.MYBLOCK_FALL);

```
- Add to src/main/resources/assets/tutorialmod/sounds/ following files:
  - myblock_break.ogg
  - myblock_step.ogg
  - myblock_place.ogg
  - myblock_hit.ogg
  - myblock_fall.ogg

- add in src/main/resources/assets/tutorialmod/sounds.json lines:
```json
,
  "myblock_break": {
    "subtitle": "sounds.tutorialmod.myblock_break",
    "sounds": [
      "tutorialmod:myblock_break"
    ]
  },
  "myblock_step": {
    "subtitle": "sounds.tutorialmod.myblock_step",
    "sounds": [
      "tutorialmod:myblock_step"
    ]
  },
  "myblock_place": {
    "subtitle": "sounds.tutorialmod.myblock_place",
    "sounds": [
      "tutorialmod:myblock_place"
    ]
  },
  "myblock_hit": {
    "subtitle": "sounds.tutorialmod.myblock_hit",
    "sounds": [
      "tutorialmod:myblock_hit"
    ]
  },
  "myblock_fall": {
    "subtitle": "sounds.tutorialmod.myblock_fall",
    "sounds": [
      "tutorialmod:myblock_fall"
    ]
  }
```