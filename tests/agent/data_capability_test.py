
ELEMENT_NAME = "test_block"
MOD_NAME = "examplemod"
MOD_ID = "examplemod"
MOD_DOMAIN = "com/example"
EXPECTED_FOLDER_PATH_STEP_1 = f"{MOD_NAME}/src/generated/resources/assets/{MOD_NAME}/blockstates"
EXPECTED_FILE_PATH_STEP_1 = EXPECTED_FOLDER_PATH_STEP_1 + f"/{ELEMENT_NAME}.json"
EXPECTED_CONTENT_STEP_1 = '''{
        "variants": {
        "": {
            "model": "$MOD_NAME:block/$ELEMENT_NAME"
            }
        }
        }'''.strip().replace("$MOD_NAME", MOD_NAME).replace("$ELEMENT_NAME", ELEMENT_NAME).replace(" ", "")
EXPECTED_FOLDER_PATH_STEP_2 = f"{MOD_NAME}/src/generated/resources/assets/{MOD_NAME}/models/block"
EXPECTED_FILE_PATH_STEP_2 = EXPECTED_FOLDER_PATH_STEP_2 + f"/{ELEMENT_NAME}.json"
EXPECTED_CONTENT_STEP_2 = '''
{
  "parent": "minecraft:block/cube_all",
  "textures": {
    "all": "$MOD_NAME:block/$ELEMENT_NAME"
  }
}
'''.strip().replace("$MOD_NAME", MOD_NAME).replace("$ELEMENT_NAME", ELEMENT_NAME).replace(" ", "")

EXPECTED_FOLDER_PATH_STEP_3 = f"{MOD_NAME}/src/generated/resources/assets/{MOD_NAME}/models/item"
EXPECTED_FILE_PATH_STEP_3 = EXPECTED_FOLDER_PATH_STEP_3 + f"/{ELEMENT_NAME}.json"
EXPECTED_CONTENT_STEP_3 = '''
{
  "parent": "$MOD_NAME:block/$ELEMENT_NAME"
}
'''.strip().replace("$MOD_NAME", MOD_NAME).replace("$ELEMENT_NAME", ELEMENT_NAME).replace(" ", "")

EXPECTED_FOLDER_PATH_STEP_4 = f"{MOD_NAME}/src/main/resources/assets/{MOD_NAME}/lang"
EXPECTED_FILE_PATH_STEP_4 = EXPECTED_FOLDER_PATH_STEP_4 + "/en_us.json"
EXPECTED_CONTAINST_STEP_4 = f'"block.{MOD_NAME}.{ELEMENT_NAME}": "Block of {ELEMENT_NAME}"'

EXPECTED_FOLDER_PATH_STEP_5 = f"{MOD_NAME}/src/main/resources/assets/{MOD_NAME}/textures/block"
EXPECTED_FILE_PATH_STEP_5 = EXPECTED_FOLDER_PATH_STEP_5 + f"/{ELEMENT_NAME}.png"

EXPECTED_FOLDER_PATH_STEP_6 = f"{MOD_NAME}/src/main/java/{MOD_DOMAIN}/{MOD_NAME}/blocks"
EXPECTED_FILE_PATH_STEP_6 = EXPECTED_FOLDER_PATH_STEP_6 + "/ModBlocks.java"
EXPECTED_CONTAINST_STEP_6 = '''
 public static final RegistryObject<Block> $ELEMENT_NAME = registerBlock("$ELEMENT_NAME",
                (properties) -> new Block(properties
                        .strength(4f).requiresCorrectToolForDrops()));'''.replace("$ELEMENT_NAME", ELEMENT_NAME).replace(" ", "")


EXPECTED = [(EXPECTED_FOLDER_PATH_STEP_1, EXPECTED_FILE_PATH_STEP_1, EXPECTED_CONTENT_STEP_1, None),
            (EXPECTED_FOLDER_PATH_STEP_2, EXPECTED_FILE_PATH_STEP_2, EXPECTED_CONTENT_STEP_2, None),
            (EXPECTED_FOLDER_PATH_STEP_3, EXPECTED_FILE_PATH_STEP_3, EXPECTED_CONTENT_STEP_3, None),
            (None, EXPECTED_FILE_PATH_STEP_4, None, EXPECTED_CONTAINST_STEP_4),
            (None, EXPECTED_FILE_PATH_STEP_5, None, None),
            (None, EXPECTED_FILE_PATH_STEP_6, None, EXPECTED_CONTAINST_STEP_6),
           ]


def get_expected_basic_block_for_step(step_index: int):
    if step_index <= len(EXPECTED):
        return EXPECTED[step_index - 1]
    else:
        raise ValueError(f"Unknown step index {step_index}")