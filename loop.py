import bpy
import string
import random
from pathlib import Path
import importlib
from config import BL_SCRIPT_FOLDER, REDIS_CODE_KEY
import asyncio
import aioredis
from functools import partial
import traceback


def file_string(file_path):
    with open(file_path) as f:
        return f.read()


def replace_main(contents, new_name="PLACEHOLDER_NAME"):
    return contents.replace('__main__', new_name)


def randomize_name(name):
    return ("neil_bl_loop_"
            + ''.join(random.choice(string.ascii_uppercase + string.digits)
                      for x in range(10))
            + "_" + name)


def copy_contents(target_path, source_path):
    with open(target_path, 'w') as f:
        f.write(file_string(source_path))


def run_script(file_path):
    file_stem = Path(file_path).stem
    new_name = randomize_name(file_stem)
    new_script_path = Path(BL_SCRIPT_FOLDER).joinpath(f"{new_name}.py")
    new_cache_folder = new_script_path.parent.joinpath('__pycache__')
    try:
        copy_contents(new_script_path, file_path)
        bpy.utils.load_scripts(refresh_scripts=True)
        importlib.import_module(new_name)
    finally:
        Path.unlink(new_script_path)
        for f in new_cache_folder.glob(f'{new_name}*'):
            Path.unlink(f)
        pass


async def run_process(process, *args):
    return await asyncio.create_subprocess_exec(process, *args,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)


async def run_redis_server():
    return await run_process('redis-server')


async def stop_redis_process(proc):
    await proc.terminate()


async def close_redis(redis):
    redis.close()
    await redis.wait_closed()


# Performs its own cleanup, in case it can't return cancel function.
async def ensure_server(redis):
    if not redis:
        redis = await aioredis.create_redis_pool('redis://localhost')
    try:
        return (redis, partial(close_redis, redis))
    except Exception:
        await close_redis(redis)
        raise Exception("Could not connect to Blend Loop server.")


async def poll_for_file_path(redis):
    response = await redis.getset(REDIS_CODE_KEY, '')
    return response.decode('utf-8') if response else ''


async def loop(state, error):
    conn, cancel = await ensure_server(state())
    file_path = await poll_for_file_path(conn)
    if file_path:
        try:
            run_script(file_path)
        except Exception as e:
            error(e)
            print('BLEND LOOP ERROR: ')
            traceback.print_exc()
    await asyncio.sleep(0.1)
    return (lambda: conn, cancel)
