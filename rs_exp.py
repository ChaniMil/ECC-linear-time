import string
import random
import time
from reedsolo import RSCodec
from experiments_linear_time import you_choose_k_exclamation_mark
from main_code import init_graphs, linear_encode, linear_decode


def main():
    r, epsilon = (0.7971014492753623, 0.14545454545454545)
    (k, pr, qr, pe, qe, b, b_padding, rate_eff) = you_choose_k_exclamation_mark(epsilon=epsilon, r=r)[0]
    print(k, pr, qr, pe, qe, b, b_padding, rate_eff)
    gr, ge = init_graphs(pr, qr, pe, qe)
    characters = string.printable  # Includes all printable characters
    random_string = ''.join(random.choice(characters) for _ in range(k))
    params = (random_string.encode(), pr, qr, pe, qe, b, epsilon, ge, gr)
    enc_start_time = time.time()
    encoded_message = linear_encode(*params)
    enc_stop_time = time.time()
    dec_start_time = time.time()
    decoded_message = linear_decode(encoded_message, *params[1:])
    dec_stop_time = time.time()
    print("LT Encoding time: ", enc_stop_time - enc_start_time)
    print("LT Decoding time: ", dec_stop_time - dec_start_time)
    if decoded_message == random_string.encode():
        print('Successful LT decoding')

    rs = RSCodec(int(k*(1-r)/r), nsize=32639)
    enc_start_time = time.time()
    enc_msg = rs.encode(random_string.encode())
    enc_stop_time = time.time()
    print("RS Encoding time: ", enc_stop_time - enc_start_time)
    dec_start_time = time.time()
    dec_msg = rs.decode(enc_msg)[0]
    dec_stop_time = time.time()
    print("RS Decoding time: ", dec_stop_time - dec_start_time)
    if enc_msg == dec_msg:
        print('Successful RS decoding')


if __name__ == '__main__':
    main()
