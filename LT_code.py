import parameters
import main_code


def slice_word(word, k):
    # slice the word by k
    sliced_word = word[0][:k]
    return sliced_word, word[1]


class LTCode:
    def __init__(self, epsilon, r, k=0, eps_dist=0.1, r_dist=0.1, prime_limit=200, max_k=15000000):
        """
        a construction for the main class of the package
        Args:
            epsilon: the distance from being optimal
            r: the rate of the code
            k: the length of the word we want to encode
            eps_dist: the distance our epsilon can be from the epsilon given
            r_dist: the distance our r can be from the r given
            prime_limit: the max value of primes for the graphs
            max_k: the max value of code dimension
        """
        self.epsilon = epsilon
        self.r = r
        if k == 0:  # no k was given
            self.k = None
            self.options = None
            self.params = None
            self.expander = None
            self.ramanujan = None
        else:
            self.k = k  # set k of the class
            self.options = parameters.choose_params(r, epsilon, eps_dist, r_dist, prime_limit, max_k)  # get list of options
            self.params = min([i for i in self.options if i[-1] >= k], key=lambda x: x[-1])  # take the minimum k
            self.ramanujan, self.expander = main_code.init_graphs(*self.params[:4])  # generate the graphs
            
    # ---------------------------------------choosing parameters-----------------------------------------------------

    def get_k_list(self, e_close=0.1, r_close=0.1, prime_limit=200, max_k=15000000):
        """
        function for the user if it doesn't want to take the minimal k
        Args:
            e_close: how close epsilon can be
            r_close: how close r can be
            prime_limit: the max value of primes for the graphs
            max_k: the max value of code dimension

        Returns:
            list of parameters the user can choose from
        """
        self.options = parameters.choose_params(self.r, self.epsilon, e_close, r_close, prime_limit, max_k)
        return self.options

    def choose_index(self, i):
        """
        a function for the user to choose from the parameters list
        Args:
            i: the index from options the user chooses

        Returns:
            the user's choice
        """
        choice = self.options[i]
        self.params = choice
        self.ramanujan, self.expander = main_code.init_graphs(*choice[:4])
        return choice

# ---------------------------------------encoding and decoding---------------------------------------------------

    def encode(self, data, r_dist=0.1, eps_dist=0.1, prime_limit=200, max_k=15000000):
        """
        encoding a word
        1. if we already chose parameters, we will encode according to them
        2. if we didn't choose parameters, we choose in the function according to the length of data
        Args:
            data: the word we want to encode
            r_dist: the allowed distance from r
            eps_dist: the allowed distance from epsilon
            prime_limit: the max value of primes for the graphs
            max_k: the max value of code dimension

        Returns:
            the encoding of the word
        """
        if self.params is None:
            # no parameters so we need to choose
            k = len(data)
            params_list = parameters.choose_params(self.r, self.epsilon, r_dist, eps_dist, prime_limit, max_k)
            params = min([p for p in params_list if p >= k], key=lambda x: x[-1])  # the first k we can encode
            expander = None
            ramanujan = None
        else:
            # copy all parameters and graphs
            params = self.params
            expander = self.expander
            ramanujan = self.ramanujan

        data = bytearray(data)
        if len(data) < params[-1]:  # if we need to pad
            data += bytearray(self.params[-1] - len(data))
        return main_code.linear_encode(data, *params[:5], params[6], ramanujan, expander)  # encode

    def decode(self, data, erase_pos=None, r_dist=0.1, eps_dist=0.1, k=0, prime_limit=200, max_k=15000000):
        """
        decoding a codeword
        1. if we already chose parameters, we will decode according to them
        2. if we didn't choose parameters, we choose in the function according to the shape of data
        Args:
            data: the codeword we want to decode
            erase_pos: the locations of the errors
            r_dist: if we choose parameters, the allowed distance from r
            eps_dist: if we choose parameters, the allowed distance from epsilon
            k: the length of the word we want to decode to
            prime_limit: the max value of primes for the graphs
            max_k: the max value of code dimension

        Returns:
            word: the word we decoded to
            flag: indicator if the program went well
        """
        if self.params is None:
            # if there are no params, generate them
            n = len(data)  # n blocks
            delta = len(data[0])  # each contains Delta symbols
            # find parameters with same delta and n
            params_list = parameters.choose_params(self.r, self.epsilon, r_dist, eps_dist, prime_limit, max_k)
            params = [p for p in params_list if p[2]+1 == delta and p[3]*(p[3]*p[3]-1) == n+n][0]
            expander = ramanujan = None  # set the graphs to be none
        else:
            # copy all the parameters and graphs
            params = self.params
            expander = self.expander
            ramanujan = self.ramanujan

        if erase_pos is None:
            erase_pos = []

        # decode
        word = main_code.linear_decode(data, params[:5], params[6], ramanujan, expander, erase_pos)
        if k != 0:  # slice the word with k
            return slice_word(word, k)
        elif self.k != 0:  # slice the word with self.k
            return slice_word(word, self.k)
        else:
            return word

# ---------------------------------------other functions---------------------------------------------------------
    
    def decoding_capability(self, errors=0, erasures=0):
        """
        how much can we correct
        Args:
            erasures: the maximum number of erasures
            errors: the maximum number of errors

        Returns:
            the number of errors and erasures we can correct
        """
        # s + 2e <= 1-r-epsilon
        r = self.params[5]
        epsilon = self.params[6]
        if errors == 0:
            return (1-r-epsilon-erasures)/2, erasures
        else:
            return errors, 1-r-epsilon-2*errors
