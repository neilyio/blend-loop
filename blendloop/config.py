import bpy
from pathlib import Path

REDIS_CODE_KEY = 'bl-queue:eval-string'
BL_SCRIPT_FOLDER = Path(bpy.utils.script_path_user()).joinpath("modules")
BL_RUN_PATH = Path("c:/Users/neilh/Desktop/blend-loop/main.py")
BL_TASK_NAME = 'BL_TASK_NAME_5152020'
