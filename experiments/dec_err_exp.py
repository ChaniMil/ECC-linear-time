import random
import string
import numpy as np
import matplotlib.pyplot as plt
import parameters
from main_code import init_graphs, linear_encode, linear_decode


def inject_errors(encoded_message, fraction_of_errors, error_type):
    """
    This function injects random errors to the message
    :param encoded_message: the codeword
    :param fraction_of_errors: the fraction of errors to inject
    :param error_type: erasures - 0, errors - 1, mixed - 2
    :return: the word with errors, the word with erasures, the position of erasures
    """
    num_of_errors = round(fraction_of_errors * len(encoded_message))
    errors_pos = random.sample(range(len(encoded_message)), num_of_errors)  # which block did the error occur
    changed_word = encoded_message.copy()
    minus = ord('-')
    # for each error type there is a different number of errors and erasures
    if error_type == 0:
        amount_of_errors = 0
    elif error_type == 1:
        amount_of_errors = num_of_errors
    else:
        amount_of_errors = num_of_errors // 2

    for idx in errors_pos[:amount_of_errors]:  # injecting the errors part
        changed_word[idx] = [random.randint(1, 255) for _ in range(len(encoded_message[0]))]
    for idx in errors_pos[amount_of_errors:]:  # injecting the erasures part
        changed_word[idx] = [minus] * len(encoded_message[0])
    # returning the word we changed and the erasures locations
    return changed_word, errors_pos[amount_of_errors:]


def success_rate_plot(r, num_simulations, encoded_msg, params, fraction_of_errors, name, error_type=1,
                      type_err='limited'):
    """
    This function calculates and plots the success rate of the code with given parameters
    """
    all_success_rates = []
    # calculating the success rate for the different error fractions
    step = fraction_of_errors[1] - fraction_of_errors[0]
    fraction_of_errors_2 = []
    frac_of_err = fraction_of_errors[0]
    j = 0
    while True:
        fraction_of_errors_2 += [frac_of_err]
        success_rates = []
        for i in range(num_simulations):
            print(j, i)
            corrupted_message, errors = inject_errors(encoded_msg, frac_of_err, error_type)
            decoded_message = bytes(linear_decode(corrupted_message, *params[1:], erasuers=errors)[0])
            original_msg = params[0]
            success_rate = 100 * (original_msg == decoded_message)
            success_rates.append(success_rate)

        print(sum(success_rates) / num_simulations)
        all_success_rates.append(sum(success_rates) / num_simulations)
        # stops simulating after two failed decoding
        if len(all_success_rates) >= 2 and all_success_rates[-1] == 0 and all_success_rates[-2] == 0:
            break
        # increments
        j += 1
        frac_of_err += step
    print(all_success_rates)

    # visualization
    epsilon = params[6]
    fraction_labels = []
    for value in fraction_of_errors_2[:len(all_success_rates)]:
        fraction_labels.append(100 * value)
    np.set_printoptions(precision=4)
    plt.figure(figsize=(10, 6))
    plt.ylim(-3, 103)
    plt.xlim(int(np.min(fraction_labels)) - 0.4, np.max(fraction_labels) + 0.4)
    # the error capability is (1-r-ε)/2
    if error_type == 1:
        plt.axvline(x=(1 - r - epsilon) * 50, ymin=0, ymax=1, color='black', ls='--', lw=1.5, label='(1-r-ε)/2')
    # the erasure capability is 1-r-ε
    if error_type == 0:
        plt.axvline(x=(1 - r - epsilon) * 100, ymin=0, ymax=1, color='black', ls='--', lw=1.5, label='1-r-ε')
    # the erasure capability is 2(1-r-ε)/3
    if error_type == 2:
        plt.axvline(x=(1 - r - epsilon) * 200 / 3, ymin=0, ymax=1, color='black', ls='--', lw=1.5, label='2(1-r-ε)/3')
    plt.legend(bbox_to_anchor=(1.0, 1), loc='best')
    steps = (int(np.max(fraction_labels)) - int(np.min(fraction_labels)) + 1) // 20 + 1
    x_ticks = np.arange(int(np.min(fraction_labels)), int(np.max(fraction_labels)) + 1, steps)
    plt.xticks(x_ticks)
    len_of_lists = max(len(fraction_labels), len(all_success_rates))
    plt.plot(fraction_labels[:len_of_lists], all_success_rates[:len_of_lists], marker='o', linestyle='-', linewidth=3)
    plt.ylabel('Success Rate [%]')
    plt.xlabel('Fraction of Noise [%]')
    if error_type == 1:
        plt.title(f'Error Correction Success Rates Across Simulations - {type_err} range'
                  f'\n{num_simulations} Trials per Error Fraction, ε={epsilon:.{4}f}, r={r:.{4}f}')
    if error_type == 0:
        plt.title(f'Erasure Correction Success Rates Across Simulations - {type_err} range'
                  f'\n{num_simulations} Trials per Error Fraction, ε={epsilon:.{4}f}, r={r:.{4}f}')
    if error_type == 2:
        plt.title(f'Mixed Correction Success Rates Across Simulations - {type_err} range'
                  f'\n{num_simulations} Trials per Error Fraction, ε={epsilon:.{4}f}, r={r:.{4}f}')
    plt.grid(True)
    plt.savefig(f"real_res/success_rates_{name}_ε={epsilon:.{4}f}_r={r:.{4}f}.png")
    plt.cla()

    capability = 1 - r - epsilon
    if error_type == 1:
        capability /= 2
    if error_type == 2:
        capability = 2 * capability / 3
    j = min([(i, abs(a - capability)) for (i, a) in enumerate(fraction_labels)], key=lambda x: x[1])[0]
    return sum(all_success_rates[j - 1:j + 2]) / 3


def run_simulations_corrupted(num_simulations, pr, qr, pe, qe, b, rate_eff, epsilon, k):
    gr, ge = init_graphs(pr, qr, pe, qe)
    # generate random word
    characters = string.printable
    random_string = ''.join(random.choice(characters) for _ in range(k))

    params = (random_string.encode(), pr, qr, pe, qe, b, epsilon, gr, ge)
    encoded_message = linear_encode(*params)

    print("extended range - errors")
    fraction_of_errors = np.linspace(0, (1 - rate_eff - epsilon), 11)
    avg = success_rate_plot(rate_eff, num_simulations, encoded_message, params, fraction_of_errors, "extended range r",
                            type_err='extended')
    # check if we should simulate the limited range
    if avg == 100 or avg == 0:
        return
    print("limited range - errors")
    fraction_of_errors = np.linspace(0.45 * (1 - rate_eff - epsilon), 0.55 * (1 - rate_eff - epsilon), 11)
    success_rate_plot(rate_eff, num_simulations, encoded_message, params, fraction_of_errors, "limited range r",
                      type_err='limited')


def run_simulations_deleted(num_simulations, pr, qr, pe, qe, b, rate_eff, epsilon, k):
    gr, ge = init_graphs(pr, qr, pe, qe)
    # generate random word
    characters = string.printable
    random_string = ''.join(random.choice(characters) for _ in range(k))

    params = (random_string.encode(), pr, qr, pe, qe, b, epsilon, gr, ge)
    encoded_message = linear_encode(*params)

    print("extended range - erasures")
    fraction_of_errors = np.linspace(0, 3 * (1 - rate_eff - epsilon), 11)
    avg = success_rate_plot(rate_eff, num_simulations, encoded_message, params, fraction_of_errors,
                            "Deletion - extended range",
                            0, type_err='extended')
    # check if we should simulate the limited range
    if avg == 100 or avg == 0:
        return
    print("limited range - erasures")
    fraction_of_errors = np.linspace(0.9 * (1 - rate_eff - epsilon), 1.1 * (1 - rate_eff - epsilon), 11)
    success_rate_plot(rate_eff, num_simulations, encoded_message, params, fraction_of_errors,
                      "Deletion - limited range", 0,
                      type_err='limited')


def run_simulations_mixed(num_simulations, pr, qr, pe, qe, b, r, epsilon, k):
    gr, ge = init_graphs(pr, qr, pe, qe)
    # generate random word
    characters = string.printable
    random_string = ''.join(random.choice(characters) for _ in range(k))

    params = (random_string.encode(), pr, qr, pe, qe, b, epsilon, gr, ge)
    encoded_message = linear_encode(*params)

    print("extended range - mixed")
    fraction_of_errors = np.linspace(0, 3 * (1 - r - epsilon), 11)
    avg = success_rate_plot(r, num_simulations, encoded_message, params, fraction_of_errors,
                            "Mixed - extended range", 2,
                            type_err='extended')
    # check if we should simulate the limited range
    if avg == 100 or avg == 0:
        return
    print("limited range - erasures")
    fraction_of_errors = np.linspace(0.6 * (1 - r - epsilon), 2.2 / 3 * (1 - r - epsilon), 11)
    success_rate_plot(r, num_simulations, encoded_message, params, fraction_of_errors, "Mixed - limited range",
                      0,
                      type_err='limited')


def find_error(codeword, params, num_of_rounds, frac_of_errors):
    """This function checks if codeword can be decoded of frac_of_err in num_of_rounds simulations"""
    failures = []
    for i in range(num_of_rounds):
        print(i)
        corrupted_message = inject_errors(codeword, frac_of_errors, 1)[0]
        decoded_message = bytes(linear_decode(corrupted_message, *params[1:])[0])
        if params[0] != decoded_message:
            failures.append(i)
            print(f'after {i} iterations, we found an error')
    print(failures)


def main():
    set_ = []
    for r in np.linspace(0.3, 0.7, 5):
        for eps in np.linspace(0.1, 0.4, 4):
            param_list = parameters.choose_params(r, eps, 0.1, 0.05)
            if param_list:
                set_.append(min(param_list, key=lambda x: x[-1]))

    for i, s in enumerate(set_):
        print(i, s)

    for s in set_:
        run_simulations_mixed(20, *s)
        run_simulations_corrupted(20, *s)
        run_simulations_deleted(20, *s)


if __name__ == '__main__':
    main()
