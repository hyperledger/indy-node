from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process

from scripts.load import put_load

num_tasks = 100
use_processes = False


if __name__ == '__main__':

    executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    with executor(max_workers=10) as e:
        for _ in range(num_tasks):
            e.submit(put_load)