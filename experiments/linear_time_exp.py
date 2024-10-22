import random
import string
from collections import defaultdict
import numpy as np
from parameters import choose_params
import time
import matplotlib.pyplot as plt
from main_code import init_graphs, linear_encode, linear_decode


def run_time_simulation(params_list, word):
    """
    This function gets a list of a few parameters sets,
    measures the encoding and decoding time, and plots the results
    """
    enc_times = []
    dec_times = []
    k_list = []
    n_list = []
    enc_graph_times = []
    dec_graph_times = []
    params_list = sorted(params_list, key=lambda x: x[-1])
    for (pr, qr, pe, qe, b, r, epsilon, k) in params_list:
        print((pr, qr, pe, qe, b, r, epsilon, k))
        word_to_encode = word[:k]
        graph_time = time.time()
        graphs = init_graphs(pr, qr, pe, qe)
        startt_time = time.time()
        code = linear_encode(word_to_encode.encode(), pr, qr, pe, qe, b, epsilon, *graphs)
        stop_time = time.time()
        enc_times.append(stop_time - startt_time)
        enc_graph_times.append(stop_time - graph_time)
        print("enc", enc_times[-1])
        print("done encoding")
        start_time = time.time()
        linear_decode(code, pr, qr, pe, qe, b, epsilon, *graphs)
        stop_time = time.time()
        dec_graph_times.append(stop_time - start_time + (startt_time - graph_time))
        dec_times.append(stop_time - start_time)
        print("dec", dec_times[-1])
        print("done decoding")
        k_list.append(k)
        n_list.append(len(code)*(pe+1))

    print("k", k_list)
    print("enc", enc_times)
    print("enc with graph", enc_graph_times)
    if k_list:
        plt.plot(k_list, enc_times, marker='o')
        plt.xlabel('k')
        plt.ylabel('Time (seconds)')
        plt.title(f'k vs Time for encode\nr ≈ 0.6')
        plt.grid(True)
        plt.savefig(f"time_simulations/plot_enc_r≈0.6.png")
        plt.cla()

        plt.plot(k_list, enc_graph_times, marker='o')
        plt.xlabel('k')
        plt.ylabel('Time (seconds)')
        plt.title(f'k vs Time for encode\nr ≈ 0.6')
        plt.grid(True)
        plt.savefig(f"time_simulations/plot_with_graph_enc_r≈0.6.png")
        plt.cla()

    if n_list:
        dec_sorted = []
        dec_graph_times_sorted = []
        n_sorted_list = sorted(n_list)
        for n in n_sorted_list:
            i = n_list.index(n)
            dec_sorted.append(dec_times[i])
            dec_graph_times_sorted.append(dec_graph_times[i])
        print("n", n_sorted_list)
        print("dec", dec_sorted)
        print("dec with graph", dec_graph_times)
        plt.plot(n_sorted_list, dec_sorted, marker='o')
        plt.xlabel('n')
        plt.ylabel('Time (seconds)')
        plt.title(f'n vs Time for decode\nr ≈ 0.6')
        plt.grid(True)
        plt.savefig(f"time_simulations/plot_dec_r≈0.6.png")
        plt.cla()

        plt.plot(n_sorted_list, dec_graph_times_sorted, marker='o')
        plt.xlabel('n')
        plt.ylabel('Time (seconds)')
        plt.title(f'n vs Time for decode\nr ≈ 0.6')
        plt.grid(True)
        plt.savefig(f"time_simulations/plot_dec_with_graph_r≈0.6.png")
        plt.cla()


def find_similar_parameters():
    """
    This function finds sets of parameters that have similar rate
    """
    params_list = []
    for i in np.arange(0.1, 0.3, 0.05):
        for j in np.arange(0.5, 0.8, 0.05):
            for pr in choose_params(j, i):
                if pr[2] != 193 or pr[3] != 13:  # 193, 13 are wrong parameters for the Ramanujan
                    params_list.append(pr)

    unique_params = []
    for pr in params_list:
        if pr not in unique_params:
            unique_params.append(pr)

    # Sort the params_list by the last element
    unique_params = sorted(unique_params, key=lambda x: x[-1])

    # Create buckets
    buckets = defaultdict(list)
    for item in unique_params:
        found_flag = False
        bucket_key = round(item[5], 1)  # Use item[5] as the key for bucketing
        for i, pr in enumerate(buckets[bucket_key]):
            if item[-1] == pr[-1]:
                if item[5] - 0.6 < pr[5] - 0.6:
                    buckets[bucket_key][i] = item
                found_flag = True
        if not found_flag:
            buckets[bucket_key].append(item)

    return buckets


def main():
    k = 15000000
    characters = string.printable
    random_string = ''.join(random.choice(characters) for _ in range(k))
    params = find_similar_parameters()[0.6]  # we choose this bucket because it has most samples
    run_time_simulation(params, random_string)


if __name__ == '__main__':
    main()
