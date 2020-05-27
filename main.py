import bpy
import sys
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
sys.path.append("c:/Users/neilh/Documents/GitHub/blend-loop")
from state import BlendLoopState
from runner import (
    loop_is_running, loop_start, loop_stop,
    error_get, error_clear, info_get, info_clear,
    directory_get, directory_set)


def _tag_redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


class BlendLoopMessageSubscriber(bpy.types.Operator):
    bl_idname = "wm.blend_loop_message_subscriber"
    bl_label = "Report Blend Loop messages"
    _timer = None

    def __init__(self):
        self._timer = bpy.context.window_manager.event_timer_add(
            0.1, window=bpy.context.window)

    def __del__(self):
        if self._timer:
            bpy.context.window_manager.event_timer_remove(self._timer)

    def modal(self, context, event):
        if event.type == 'TIMER':
            if info_get():
                self.report({'INFO'}, "BLEND LOOP: " + str(info_get()))
                info_clear()
            if error_get():
                self.report({'ERROR'}, "BLEND LOOP: " + str(error_get()))
                error_clear()
        return {'PASS_THROUGH'}

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class BlendLoopToggle(bpy.types.Operator):
    bl_idname = "wm.blend_loop_toggle"
    bl_label = "Start Blend Loop"
    bl_description = "Toggle Blend Loop to watch for file changes."

    def execute(self, context):
        if loop_is_running():
            loop_stop()
        else:
            loop_start()
        _tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class BlendLoopPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Blend Loop"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        on = loop_is_running()

        row = self.layout.row()
        row.operator("wm.blend_loop_toggle",
                     text="Blend Loop ON" if on else "Blend Loop OFF",
                     depress=on,
                     icon='PREVIEW_RANGE')

        row = self.layout.row()
        if not directory_get():
            row.operator("wm.blend_loop_directory_load",
                         text="",
                         icon='FILEBROWSER')
            row.label(text="...")
        else:
            row.operator("wm.blend_loop_directory_clear",
                         text="",
                         icon='X')
            row.label(text=directory_get())


class BlendLoopStateProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="")
    b: bpy.props.BoolProperty(default=False)
    i: bpy.props.IntProperty(default=0)
    s: bpy.props.StringProperty(default="")


class BlendLoopDirectoryLoad(bpy.types.Operator):
    bl_idname = "wm.blend_loop_directory_load"
    bl_label = "Load Directory Path"
    bl_description = "Load all Scripts from a Directory"

    # fileselect_add automatically assigns to a property.
    # 'directory', 'filepath', 'filename', 'files' are all valid.
    # Whichever one is present will dictate what the filebrowser allows.
    directory: bpy.props.StringProperty(
        name="Directory Path",
        description="BlendLoopDirectory Load field")

    def execute(self, context):
        path = Path(self.directory)
        if path.exists():
            directory_set(path)
        _tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BlendLoopDirectoryClear(bpy.types.Operator):
    bl_idname = "wm.blend_loop_directory_clear"
    bl_label = "Clear Directory Path"
    bl_description = "Clear the Blend Loop Directory Path"

    def execute(self, context):
        directory_set("")
        _tag_redraw()
        return {'FINISHED'}


def register():
    wm = bpy.types.WindowManager
    bpy.utils.register_class(BlendLoopDirectoryLoad)
    bpy.utils.register_class(BlendLoopDirectoryClear)
    bpy.utils.register_class(BlendLoopStateProperty)
    bpy.utils.register_class(BlendLoopPanel)
    bpy.utils.register_class(BlendLoopToggle)
    bpy.utils.register_class(BlendLoopMessageSubscriber)
    wm.blend_loop_state_property = bpy.props.CollectionProperty(
        type=BlendLoopStateProperty)
    wm.blend_loop_state = BlendLoopState(
        bpy.context.window_manager.blend_loop_state_property)
    wm.blend_loop_state.subscriber = (
        bpy.ops.wm.blend_loop_message_subscriber())


def unregister():
    del bpy.types.WindowManager.blend_loop_state
    del bpy.types.WindowManager.blend_loop_state_property
    bpy.utils.unregister_class(BlendLoopDirectoryLoad)
    bpy.utils.unregister_class(BlendLoopDirectoryClear)
    bpy.utils.unregister_class(BlendLoopState)
    bpy.utils.unregister_class(BlendLoopPanel)
    bpy.utils.unregister_class(BlendLoopToggle)
    bpy.utils.unregister_class(BlendLoopMessageSubscriber)


if __name__ == '__main__':
    register()
