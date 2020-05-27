import bpy
import string
import random
from pathlib import Path
import importlib
from contextlib import asynccontextmanager
from .config import BL_SCRIPT_FOLDER, REDIS_CODE_KEY
import asyncio
import aiofiles
import aioredis
from functools import partial
import traceback


async def file_string(file_path):
    async with aiofiles.open(file_path) as f:
        return await f.read()


def replace_main(contents, new_name="PLACEHOLDER_NAME"):
    return contents.replace('__main__', new_name)


def randomize_name(name):
    return ("bl_loop_"
            + ''.join(random.choice(string.ascii_uppercase + string.digits)
                      for x in range(10))
            + "_" + name)


async def copy_contents(target_path, source_path):
    async with aiofiles.open(target_path, 'w') as f:
        await f.write(await file_string(source_path))


async def copy_folder(target_path, source_path):
    target = Path(target_path)
    source = Path(source_path)
    target.mkdir(exist_ok=True)
    for child in Path(source).iterdir():
        if child.is_dir():
            await copy_folder(target.joinpath(child.name), child)
        else:
            await copy_contents(target.joinpath(child.name), child)


def delete_folder(target_path):
    # Make sure we're somewhere in the Blender modules folder.
    assert target_path.relative_to(BL_SCRIPT_FOLDER)
    target = Path(target_path)
    for child in target.iterdir():
        if child.is_dir():
            delete_folder(child)
        else:
            Path.unlink(child)
    Path.rmdir(target)


@asynccontextmanager
async def temp_copy(target_path, source_path):
    target = Path(target_path)
    source = Path(source_path)
    if source.is_dir():
        await copy_folder(target, source)
        yield
        delete_folder(target)
    else:
        await copy_contents(target, source)
        yield
        Path.unlink(target)


async def run_script(path):
    name = Path(path).name
    target_path = Path(BL_SCRIPT_FOLDER).joinpath(randomize_name(name))
    async with temp_copy(target_path, path):
        bpy.utils.load_scripts(refresh_scripts=True)
        importlib.import_module(target_path.stem)


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


async def poll_for_signal(redis):
    response = await redis.getset(REDIS_CODE_KEY, '')
    return response.decode('utf-8') if response else ''


async def loop(state, error, info, directory_path):
    conn, cancel = await ensure_server(state())
    if await poll_for_signal(conn):
        try:
            # Will import the directory path
            # even if file_path is not in directory.
            if not (Path(directory_path).exists() and len(directory_path) > 0):
                raise FileNotFoundError(
                    f'Directory path is not valid: "{directory_path}"')
            await run_script(directory_path)
            info(f"Ran '{Path(directory_path).stem}'")
        except Exception as e:
            error(e)
            print('BLEND LOOP ERROR: ')
            traceback.print_exc()
            print("\n\n")
    await asyncio.sleep(0.1)
    return (lambda: conn, cancel)
