import reedsolo
from reedsolo import RSCodec
from expander_code import decode_expander, encode_expander
from left_code import encode_ramanujan, decode_ramanujan
from explicit_ramanujan_construction import ramanujan
from datetime import datetime


def init_graphs(pr, qr, pe, qe):
    expander_graph = ramanujan(pe, qe)
    ramanujan_graph = ramanujan(pr, qr)
    return ramanujan_graph, expander_graph


def linear_encode(message_to_encode, pr, qr, pe, qe, b, epsilon, ramanujan_graph=None, expander_graph=None):
    """
    Encodes a given word in linear time, using a combination of Ramanujan graphs and Reed-Solomon codes.
    Process overview:
        1. Left code: Applies encoding via Ramanujan graph and Reed-Solomon.
        2. Block encoding: Splits the word into blocks and encodes each with a Reed-Solomon code.
        3. Expander code: Rearrange the order of the symbols, to deal bursts of errors efficiently.
    :param message_to_encode: The message to be encoded
    :param pr: 'p' parameter for the ramanujan graph
    :param qr: 'q' parameter for the ramanujan graph
    :param pe: 'p' parameter for the expander graph
    :param qe: 'q' parameter for the expander graph
    :param epsilon: Small value related to the distance of the code
    :param b: The size of each block before Reed-Solomon encoding
    :param expander_graph: Optional pre-initialized expander graph
    :param ramanujan_graph: Optional pre-initialized Ramanujan graph.
    :return: Systematic encoding presented as a list of blocks
    """
    # Left code
    if ramanujan_graph is None:
        ramanujan_graph = ramanujan(pr, qr)  # generate the ramanujan graph
    partially_encoded_msg = encode_ramanujan(ramanujan_graph, message_to_encode, epsilon / 32)

    # Block encoding: Split word into blocks and apply Reed-Solomon encoding
    if expander_graph is None:
        expander_graph = ramanujan(pe, qe)  # generate the expander graph
    n = expander_graph.num_of_nodes // 2  # nodes on each side of the expander
    delta = expander_graph.degree
    rsc3 = RSCodec(int(delta - b), nsize=255)  # Initialize Reed-Solomon code

    # Split the encoded word into blocks of size b
    blocks = [partially_encoded_msg[b * i:b * (i + 1)] for i in range(n)]

    # Ensure all blocks have the correct length, padding where necessary
    # idx will be the first block to pad
    idx = 0
    for bl in blocks:
        idx += 1
        if len(bl) != b:
            break

    blocks[idx - 1] += bytearray(b - len(blocks[idx - 1]))
    empty_block = bytearray(b)
    for i in range(idx, len(blocks)):
        blocks[i] = empty_block

    # Apply Reed-Solomon encoding to each block
    blocks = [rsc3.encode(bl) for bl in blocks]

    # Expander code: Apply expander graph encoding to the blocks
    code = encode_expander(expander_graph, blocks)
    return code


def linear_decode(encoded_message, pr, qr, pe, qe, b, epsilon, ramanujan_graph=None, expander_graph=None, erasures=[]):
    """
    Decodes a given encoded word in linear time, using a combination of Ramanujan graphs and Reed-Solomon codes.
    Process overview:
        1. Expander code: Rearranging the codeword using an expander graph.
        2. Block decoding: Applies Reed-Solomon decoding to each block.
        3. Left code: Decodes the concatenated blocks using a Ramanujan graph and Reed-Solomon.
    :param encoded_message: The encoded message to decode.
    :param pr: 'p' parameter for the ramanujan graph
    :param qr: 'q' parameter for the ramanujan graph
    :param pe: 'p' parameter for the expander graph
    :param qe: 'q' parameter for the expander graph
    :param epsilon: Small value related to the distance of the code
    :param b: The size of each block before Reed-Solomon encoding
    :param expander_graph: Optional pre-initialized expander graph
    :param ramanujan_graph: Optional pre-initialized Ramanujan graph.
    :return: the decoded word
    """

    # Expander graph decoding
    if expander_graph is None:
        expander_graph = ramanujan(pe, qe)
    partially_decoded_msg, new_erasures = decode_expander(expander_graph, encoded_message, erasures)

    # Block decoding using Reed-Solomon
    delta = expander_graph.degree
    rsc3 = RSCodec(int(delta - b), nsize=255)
    blocks = [-1] * len(partially_decoded_msg)

    # trying to decode each of the blocks
    for i, block in enumerate(partially_decoded_msg):
        try:
            blocks[i] = rsc3.decode(block, erase_pos=new_erasures[i])[0]
        except reedsolo.ReedSolomonError:
            blocks[i] = block[:b]  # if it couldn't decode, arbitrary block
            for ep in new_erasures[i]:
                block[ep] = 0

    # concatenate the blocks
    num_of_blocks = len(blocks)
    word = [-1] * (b * num_of_blocks)
    i = 0
    for block in blocks:
        word[i:i + b] = block
        i += b

    # re-split the blocks
    if ramanujan_graph is None:
        ramanujan_graph = ramanujan(pr, qr)  # generate the ramanujan graph
    gamma = epsilon / 4
    d = ramanujan_graph.degree
    N = ramanujan_graph.num_of_nodes // 2
    k = ramanujan_graph.num_of_edges
    half_gamma_d = round(gamma * d + 0.5) // 2

    codeword = (word[:k], [word[k + half_gamma_d * i: k + half_gamma_d * (i + 1)] for i in range(2 * N)])

    # left code
    word = decode_ramanujan(ramanujan_graph, codeword, gamma / 8)
    return word


def print_info(params):
    print("------------------------------")
    print("Linear Time Code")
    date_ = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(date_)
    q = params[2]
    n = q*(q*q-1)
    print(f"Rate = {params[4]}\nepsilon = {params[5]}\n"
          f"Code can correct: {(1-params[4]-params[5])*100}% of errors")
    print(f"Alphabet size of message: 2^8\nAlphabet size of code: 2^{8+params[1]+1}")
    print(f"Message length: {params[-1]}\nCode Length: {n}")
    print(f"Ramanujan graph: {n} nodes, {n//2*(params[0]+1)} edges\n"
          f"Expander graph: {n} nodes, {n//2*(params[1]+1)} edges")
    print("------------------------------")
