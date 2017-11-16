#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

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
    print('Executing {} tasks for a process with {} threads'.format(
        num_tasks, num_threads))
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

    # TODO: WIP

    num_tasks = 10000
    num_procs = 4
    threads_per_proc = 10

    tasks_per_proc = int(math.ceil(num_tasks / num_procs))

    futrs = []
    with ProcessPoolExecutor(max_workers=num_procs) as pe:
        for _ in range(num_procs):
            fut = pe.submit(_task_for_proc, (threads_per_proc, tasks_per_proc))
            futrs.append(fut)
        print('Waiting for futures: main')
        concurrent.futures.wait(futrs)


if __name__ == '__main__':
    soft_blow()
