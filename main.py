import bpy
import sys
from pathlib import Path
sys.path.append("c:/Users/neilh/Documents/GitHub/blend-loop")
from state import BlendLoopState
from runner import (
    loop_is_running, loop_start, loop_stop,
    error_get, error_clear, info_get, info_clear)


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

    def execute(self, context):
        if loop_is_running():
            loop_stop()
        else:
            loop_start()
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


class BlendLoopStateProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="")
    b: bpy.props.BoolProperty(default=False)
    i: bpy.props.IntProperty(default=0)
    s: bpy.props.StringProperty(default="")


def register():
    wm = bpy.types.WindowManager
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
    bpy.utils.unregister_class(BlendLoopState)
    bpy.utils.unregister_class(BlendLoopPanel)
    bpy.utils.unregister_class(BlendLoopToggle)
    bpy.utils.unregister_class(BlendLoopMessageSubscriber)


if __name__ == '__main__':
    register()
