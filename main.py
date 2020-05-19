import bpy
import sys
sys.path.append("c:/Users/neilh/Documents/GitHub/blend-loop")
from runner import (
    loop_is_running, loop_start, loop_stop,
    error_get, error_clear, info_get, info_clear)


class BlendLoopErrorSubscriber(bpy.types.Operator):
    bl_idname = "wm.blend_loop_error_subscriber"
    bl_label = "Report Blend Loop error"
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


def register():
    wm = bpy.types.WindowManager
    wm.blend_loop_is_running = bpy.props.BoolProperty(default=False)
    wm.blend_loop_error = bpy.props.StringProperty(default="")
    wm.blend_loop_info = bpy.props.StringProperty(default="")
    bpy.utils.register_class(BlendLoopPanel)
    bpy.utils.register_class(BlendLoopToggle)
    bpy.utils.register_class(BlendLoopErrorSubscriber)
    bpy.ops.wm.blend_loop_error_subscriber()


def unregister():
    del bpy.types.WindowManager.blend_loop_is_running
    del bpy.types.WindowManager.blend_loop_error_message
    bpy.utils.unregister_class(BlendLoopPanel)
    bpy.utils.unregister_class(BlendLoopToggle)
    bpy.utils.unregister_class(BlendLoopErrorSubscriber)


if __name__ == '__main__':
    register()
