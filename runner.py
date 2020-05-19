import asyncio
import bpy
from blender_cloud import async_loop
from loop import loop

__task = None


async def maybe_await(func, *args):
    # Check if this is a partial object.
    # Before Python3.8, you can't await a partial function.
    if hasattr(func, 'func'):
        await maybe_await(func.func, *func.args, *args)
    elif asyncio.iscoroutinefunction(func):
        await func(*args)
    else:
        func(*args)


async def run_loop_until(error,
                         state=lambda: None, cancel=lambda: None):
    try:
        while True:
            state, cancel = await loop(state, error)
    except Exception as e:
        await maybe_await(cancel)
        error(e)
        raise


def loop_is_running():
    global __task
    if not __task:
        return False
    if __task.cancelled() or __task.done():
        return False
    return True


def loop_start():
    global __task
    if loop_is_running():
        raise Exception("Loop is already running!")
    async_task = asyncio.ensure_future(
        run_loop_until(report_error))
    async_task.add_done_callback(done_callback)
    async_loop.ensure_async_loop()
    bpy.context.window_manager.blend_loop_is_running = True
    __task = async_task


def loop_stop():
    global __task
    if not loop_is_running():
        raise Exception("Not running loop!")
    bpy.context.window_manager.blend_loop_is_running = False
    __task.cancel()


def done_callback(task):
    print("Blend Loop Closed.")


def report_error(error):
    bpy.context.window_manager.blend_loop_error_message = (
        str(error))
