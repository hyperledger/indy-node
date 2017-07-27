import concurrent
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

import math

import os

from scripts.load import put_load


# Each task is a call to `put_load`

def soft_blow(num_tasks=100, use_processes=False):
    executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    with executor(max_workers=10) as e:
        for _ in range(num_tasks):
            e.submit(put_load)


# Defining at module level so it can be pickled
def _task_for_proc(num_threads, num_tasks):
    print('Executing {} tasks for a process with {} threads'.format(num_tasks, num_threads))
    futrs = []
    with ThreadPoolExecutor(max_workers=num_threads) as te:
        for _ in range(num_tasks):
            fut = te.submit(put_load)
            futrs.append(fut)
        print('Waiting for futures: {}'.format(os.getpid()))
        concurrent.futures.wait(futrs)


def hard_blow():
    # Note: This method might perform more tasks then `num_tasks`,
    # if the values of `num_tasks`, `num_threads` are chosen such that they
    # are not multiples of `num_procs`

    num_tasks = 10000
    num_procs = 4
    threads_per_proc = 10

    tasks_per_proc = int(math.ceil(num_tasks/num_procs))

    futrs = []
    with ProcessPoolExecutor(max_workers=num_procs) as pe:
        for _ in range(num_procs):
            fut = pe.submit(_task_for_proc, (threads_per_proc, tasks_per_proc))
            futrs.append(fut)
        print('Waiting for futures: main')
        concurrent.futures.wait(futrs)


if __name__ == '__main__':
    soft_blow()
