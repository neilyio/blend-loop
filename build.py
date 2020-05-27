import sys
from pathlib import Path
from zipfile import ZipFile
from argparse import ArgumentParser

SOURCE = Path.cwd().joinpath('blendloop')
TARGET = Path.cwd().parent.joinpath('blend-loop-release.zip')


def run_clean(target_path):
    if target_path.exists():
        Path.unlink(target_path)


def run_build(target_path, source_path):
    if target_path.exists():
        raise FileExistsError(f"Build archive already exists: {target_path}")
    with ZipFile(target_path, 'w') as z:
        for i in source_path.glob('**/*'):
            z.write(i, arcname=i.relative_to(source_path.parent))


if __name__ == '__main__':
    if not sys.version_info.major == 3:
        raise RuntimeError('This script must be run with Python 3.')

    parser = ArgumentParser(
        usage='%(prog)s [options]',
        description="Build .zip file for Blender installation.")

    parser.add_argument('-c', '--clean', action='store_true', default=False)
    args = parser.parse_args()

    if args.clean:
        run_clean(TARGET)
    else:
        run_build(TARGET, SOURCE)
