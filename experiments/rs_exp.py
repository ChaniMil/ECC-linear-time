import time
from reedsolo import RSCodec
from parameters import choose_params_by_code_dimension
from main_code import init_graphs, linear_encode, linear_decode

CODE_DIMENSION = 80808
C_EXP = 17  # block size for RS - 2^c_exp - 1


def main():
    # parameters
    pr, pe, q, b, r, epsilon, k = choose_params_by_code_dimension(CODE_DIMENSION)
    qr = qe = q
    print(pr, qr, pe, qe, b, r, epsilon, k)

    msg_to_encode = 'A' * k

    # LT setup
    gr, ge = init_graphs(pr, qr, pe, qe)  # graphs
    params = (msg_to_encode.encode(), pr, qr, pe, qe, b, epsilon, gr, ge)

    # LT encoding
    enc_start_time = time.time()
    encoded_message = linear_encode(*params)
    enc_stop_time = time.time()
    print("LT Encoding time: ", enc_stop_time - enc_start_time)

    # LT decoding
    dec_start_time = time.time()
    linear_decode(encoded_message, *params[1:])
    dec_stop_time = time.time()
    print("LT Decoding time: ", dec_stop_time - dec_start_time)

    # RS setup
    rate = r  # can be r + epsilon, for different comparison
    redundancy_length = int(k / rate) - k
    msg_to_encode = 'A' * k
    rs = RSCodec(redundancy_length, c_exp=C_EXP)

    # RS encoding
    enc_start_time = time.time()
    enc_msg = rs.encode(msg_to_encode.encode('utf-8'))  # Encode as bytes
    enc_stop_time = time.time()
    print("RS Encoding time: ", enc_stop_time - enc_start_time)

    # RS decoding
    dec_start_time = time.time()
    rs.decode(enc_msg)
    dec_stop_time = time.time()
    print("RS Decoding time: ", dec_stop_time - dec_start_time)


if __name__ == '__main__':
    main()
