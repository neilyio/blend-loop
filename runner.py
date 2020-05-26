import asyncio
import bpy
from functools import wraps
from blender_cloud import async_loop
from loop import loop

__task = None


def state(func):
    @wraps(func)
    def state_wrapper(*args, **kwargs):
        state = bpy.context.window_manager.blend_loop_state
        return func(state, *args, **kwargs)
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


async def run_loop_until(error,
                         info,
                         state=lambda: None, cancel=lambda: None):
    try:
        while True:
            state, cancel = await loop(state, error, info)
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


@state
def loop_start(state):
    global __task
    if loop_is_running():
        raise Exception("Loop is already running!")
    async_task = asyncio.ensure_future(
        run_loop_until(error_set, info_set))
    async_task.add_done_callback(done_callback)
    async_loop.ensure_async_loop()
    state.is_running = True
    __task = async_task


@state
def loop_stop(state):
    global __task
    if not loop_is_running():
        raise Exception("Not running loop!")
    state.is_running = False
    __task.cancel()


def done_callback(task):
    print("Blend Loop Closed.")


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
