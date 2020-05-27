import asyncio
import bpy
from functools import wraps
from blender_cloud import async_loop
from loop import loop


def state(func):
    @wraps(func)
    def state_wrapper(*args, **kwargs):
        state = bpy.context.window_manager.blend_loop_state
        return func(state, *args, **kwargs)

    @wraps(func)
    async def async_state_wrapper(*args, **kwargs):
        state = bpy.context.window_manager.blend_loop_state
        return await func(state, *args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return async_state_wrapper
    return state_wrapper


async def maybe_await(func, *args):
    # Check if this is a partial object.
    # Before Python3.8, you can't await a partial function.
    if hasattr(func, 'func'):
        await maybe_await(func.func, *func.args, *args)
    elif asyncio.iscoroutinefunction(func):
        await func(*args)
    else:
        func(*args)


def done_callback(task):
    print("Blend Loop Closed.")


async def loop_container(state, loop_state):
    return await loop(loop_state, error_set, info_set,
                      directory_get())


@state
async def run_loop(state, loop_state=lambda: None, cancel=lambda: None):
    try:
        while True:
            loop_state, cancel = await loop_container(state, loop_state)
    except Exception as e:
        await maybe_await(cancel)
        error_set(e)
        raise


@state
def loop_is_running(state):
    if not state.task:
        return False
    if state.task.cancelled() or state.task.done():
        return False
    return True


@state
def loop_start(state):
    if loop_is_running():
        raise Exception("Loop is already running!")
    state.subscriber = bpy.ops.wm.blend_loop_message_subscriber()
    async_task = asyncio.ensure_future(run_loop())
    async_task.add_done_callback(done_callback)
    async_loop.ensure_async_loop()
    state.is_running = True
    state.task = async_task


@state
def loop_stop(state):
    if not loop_is_running():
        raise Exception("Not running loop!")
    state.is_running = False
    state.task.cancel()
    state.subscriber_clear()


@state
def error_set(state, error):
    state.error = str(error)


@state
def error_get(state):
    return state.error


def error_clear():
    error_set("")


@state
def info_set(state, info):
    state.info = str(info)


@state
def info_get(state):
    return state.info


def info_clear():
    info_set("")


@state
def directory_get(state):
    return state.directory


@state
def directory_set(state, path):
    state.directory = str(path)
