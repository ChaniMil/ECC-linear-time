def primes_1_mod_4(limit):
    """
    This function generate a list of prime numbers up to `limit` that are equivalent to 1 mod 4
    :param limit: The upper limit to generate prime numbers.
    :return: A list of prime numbers that are 1 mod 4.
    """
    if limit < 2:  # there are no primes
        return []

    sieve = [True] * (limit + 1)  # sieve of Eratosthenes to identify primes
    sieve[0] = sieve[1] = False  # 0 and 1 are not prime numbers

    for start in range(2, int(limit ** 0.5) + 1):
        if sieve[start]:
            # mark multiples of the current prime as non-prime
            for multiple in range(start * start, limit + 1, start):
                sieve[multiple] = False

    primes_1_mod_4_list = [num for num in range(2, limit + 1) if sieve[num] and num % 4 == 1]
    return primes_1_mod_4_list


def check_legendre_symbols(p, q):
    """
    This function calculate the legendre symbol of (p/q)
    :param p: a prime number
    :param q: a prime number
    :return: True if (p/q) = -1, False otherwise
    """
    symbol = pow(q, (p-1)//2, p)
    if symbol == p-1:
        return True
    return False


def find_k_p_q(limit):
    """
    This function finds pairs of p, q - primes 1 mod 4 with legendre symbol -1, that can be used for Ramanujan graph
    :param limit: The upper limit to generate prime numbers.
    :return:
        - k_p_q_dict: A dictionary where the key is k, and the value is a list [p, q].
        - dict_p_q: A dictionary where the key is q, and the value is a list of primes p matching q.
        - dict_q_p: A dictionary where the key is p, and the value is a list of primes q matching p.
    """
    primes_1_mod_4_list = primes_1_mod_4(limit)
    data = []
    dict_p_q = {}  # a dictionary with key q and value is list of ps matching for q
    dict_q_p = {}

    # generate the dict_p_q
    for q in primes_1_mod_4_list:
        dict_p_q[q] = []
        for p in primes_1_mod_4_list[8:]:  # we pick d > 64
            if check_legendre_symbols(p, q) and p + 1 < q * (q * q - 1):
                k = q * (q * q - 1) * (p + 1) // 2
                n = q * (q * q - 1)
                degree = p + 1
                if p == 193 and q == 13:  # this graph is not ramanujan
                    continue
                dict_p_q[q].append(p)
                data.append([p, q, k, n, degree])

    # generate the dict_q_p
    for p in primes_1_mod_4_list[8:]:
        dict_q_p[p] = []
        for q in primes_1_mod_4_list:  # we pick d > 64
            if check_legendre_symbols(p, q):
                if p == 193 and q == 13:  # this graph is not ramanujan
                    continue
                dict_q_p[p].append(q)

    data.sort(key=lambda x: x[2])  # sort the data by the value of k
    k_p_q_dict = {lst[2]: [lst[0], lst[1]] for lst in data}  # key = k, values = [p,q]
    return k_p_q_dict, dict_p_q, dict_q_p


def choose_params_by_code_dimension(k, prime_limit=200):
    """
    This function finds the fitting parameters for a given length of k - with the assumption thar qr = qp,
    meaning the num of vertices in the expander is identical to the num of vertices in the ramanujan
    :param k: code dimension - the length of the message to encode
    :param prime_limit: the max value of primes for the graphs
    :return: parameters for the graphs, b - the length of the blocks, r - rate of code, epsilon
             and the closest length of the word we can encode
    """
    k_p_q_dict, ps_for_each_q, _ = find_k_p_q(prime_limit)
    list_of_ks = k_p_q_dict.keys()
    # find the closest value of k that can be encoded
    at_least_k = 0
    for edges in list_of_ks:
        if edges >= k:
            at_least_k = edges
            break

    p_r, q = k_p_q_dict[at_least_k]  # find the p, q matching to k
    d = p_r + 1
    epsilon = 16 * (d // 64) / d  # define epsilon close to 0.25 and epsilon/32*d to be int, for the RS
    n_tag = (1 + epsilon / 4) * at_least_k  # the length of the word after the left code
    n = q * (q*q - 1) // 2  # number of vertices in each side, number of blocks
    b = int(n_tag // n)  # size of each block

    # find the matching p for the expander, s.t delta > b and r + epsilon < 1
    p_e = 0
    ps_for_q = ps_for_each_q[q]
    for p in ps_for_q:
        if p + 1 > b:
            if 4 * b / ((p + 1) * (4 + epsilon)) + epsilon < 1:  # verify that r + epsilon < 1
                p_e = p
                break
    if p_e == 0:
        return choose_params_by_code_dimension(at_least_k + 1)
    delta = p_e + 1
    r = 4 * b / (delta * (4 + epsilon))
    return p_r, p_e, q, b, r, epsilon, at_least_k


def choose_params_by_exact_rate_epsilon(epsilon, r, padding=False, prime_limit=200, max_k=15000000):
    """
    This function finds fitting parameters for epsilon and r given,
    note that epsilon and r are not changed during this function
    :param epsilon: the distance from MDS code
    :param r: code rate
    :param padding: whether to pad the message
    :param prime_limit: the max value of primes for the graphs
    :param max_k: the max value of code dimension
    :return: list with different parameters for the code
    """
    k_p_q_dict, ps_for_each_q, qs_for_each_p = find_k_p_q(prime_limit)  # dictionaries used
    k_list = []
    for k in k_p_q_dict.keys():
        if k > max_k:
            continue
        pr, qr = k_p_q_dict[k]
        n_tag = (1 + epsilon / 4) * k  # number of symbols after the left code
        r_tag = (1 + epsilon / 4) * r  # rate of the third RS (on the blocks)
        delta_n = k / r  # number of symbols over GF(q) in the final codeword
        if n_tag - int(n_tag) != 0:  # n_tag should be whole
            continue
        # find p, q for the expander
        for pe in qs_for_each_p.keys():
            for qe in qs_for_each_p[pe]:
                n = qe * (qe * qe - 1) // 2  # number of blocks (same as nodes in one side of expander)
                delta = pe + 1  # number of symbols on the encoded block (same as degree of expander)
                if n < delta:  # not enough nodes for the degree
                    continue
                b = int(r_tag * delta)
                b_padding = r_tag * delta - n_tag / n
                # the second condition is to make sure that the padding is not very big
                if delta * n >= delta_n and b_padding < delta // 16:
                    rate_eff = k / (delta * n)
                    if not padding:
                        if b_padding == 0.0:
                            k_list.append((k, pr, qr, pe, qe, b, b_padding, rate_eff))
                    else:
                        k_list.append((k, pr, qr, pe, qe, b, b_padding, rate_eff))
    return k_list


def choose_params(r, epsilon, r_dist=0.1, eps_dist=0.1, prime_limit=200, max_k=15000000):
    """
    This function finds the fitting parameters
    :param r: rate wanted
    :param epsilon: epsilon wanted
    :param r_dist: max distance from r wanted
    :param eps_dist: max distance from epsilon wanted
    :param prime_limit: the max value of primes for the graphs
    :param max_k: the max value of code dimension
    :return: list with fitting parameters
    """
    k_p_q_dict, ps_for_each_q, qs_for_each_p = find_k_p_q(prime_limit)  # dictionaries used
    d_list = [p+1 for p in qs_for_each_p.keys()]
    good_prs = []
    for d in d_list:
        epsilon_opt = 32 * round(epsilon*d/32) / d  # create epsilon that satisfies epsilon/32*d is whole
        if epsilon_opt != 0 and abs(epsilon-epsilon_opt) < eps_dist:
            good_prs.append((d-1, epsilon_opt))

    params = []
    for pr, epsilon_opt in good_prs:
        q_list = qs_for_each_p[pr]
        for q in q_list:
            k = q * (q*q - 1) * (pr + 1) // 2
            if k > max_k:  # takes very long time to encode
                continue
            n_tag = (1 + epsilon_opt / 4) * k  # the length of the word after the left code
            n = q * (q*q - 1) // 2  # number of vertices in each side, number of blocks
            b = round(n_tag / n)  # the size of each block

            # find the matching p for the expander, s.t delta > b and r + epsilon < 1
            ps_for_q = ps_for_each_q[q]
            for p in ps_for_q:  # the list is sorted
                r_opt = 4*b/((p + 1)*(4+epsilon_opt))
                if r_opt+epsilon_opt < 1 and r_opt > r and r_opt-r < r_dist:
                    params.append((pr, q, p, q, b, r_opt, epsilon_opt, k))
    return params
