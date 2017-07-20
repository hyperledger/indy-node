from multiprocessing import Pool, Process

from scripts.load import put_load

num_processes = 10


if __name__ == '__main__':
    # with Pool(num_processes) as p:
    #     p.map(put_load, [])
    processes = []
    for _ in range(num_processes):
        p = Process(target=put_load, )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()