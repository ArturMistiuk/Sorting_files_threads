import argparse
import logging
from pathlib import Path
from shutil import move
from threading import Thread, Semaphore

# Block with parsing arguments
parser = argparse.ArgumentParser(description='Console app for sorting files in threads.')
parser.add_argument('-s', '--source', required=True)
parser.add_argument('-o', '--output', default='sorted')
args = vars(parser.parse_args())
source = args.get('source')
output = args.get('output')


# list with all the folders
paths_to_folders = []
locker = Semaphore(4)


def get_folders_paths(path: Path):
    for item in path.iterdir():
        if item.is_dir():
            paths_to_folders.append(item)
            get_folders_paths(item)


def sort_files(path: Path):
    with locker:
        for item in path.iterdir():
            if item.is_file():
                file_ext = item.suffix
                new_path = output_folder / file_ext
                try:
                    new_path.mkdir(exist_ok=True, parents=True)
                    move(item, new_path)
                except OSError as e:
                    logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s: %(message)s")
    directory_path = Path(source)
    output_folder = Path(output)

    paths_to_folders.append(directory_path)
    get_folders_paths(directory_path)

    threads = []

    for folder in paths_to_folders:
        thread = Thread(target=sort_files, args=(folder, ))
        threads.append(thread)
        thread.start()
        
    [thread.join() for thread in threads]
