import reedsolo
from reedsolo import RSCodec
from LinkedList import LinkedList


def encode_ramanujan(graph, word, gamma_tag):
    """
    This function encodes each of the vertices with systematic MDS,
    and then encodes the redundancy with rate 1/4 Reed Solomon
    :param graph: Ramanujan graph
    :param word: word to encode - must be the same length as the num of edges
    :param gamma_tag: the rate of the first Reed Solomon??
    :return: a systematic codeword - the original word concatenated to all the redundancies
    """
    # graph stuff
    m = graph.num_of_edges
    d = graph.degree
    edges = graph.edges()  # the edges [[x,y]...[z,w]]

    # encoding stuff
    vertices = [bytearray(d) for _ in range(graph.num_of_nodes)]  # each node holds a word to encode
    symbol_counter = [0] * graph.num_of_nodes

    # putting the symbols of the word in the vertices
    for (node1, node2), symbol in zip(edges, word):
        vertex_index = symbol_counter[node1]
        vertices[node1][vertex_index] = symbol  # append the symbol on the edge to the list of x
        vertex_index = symbol_counter[node2]
        vertices[node2][vertex_index] = symbol  # append the symbol on the edge to the list of y
        symbol_counter[node1] += 1
        symbol_counter[node2] += 1

    # the reed solomons
    nodeword_length = round(4*d*gamma_tag)  # the length of the codeword on each node
    rsc1_redundancy = round(gamma_tag*d + 0.5)
    rsc2_redundancy = int(nodeword_length - rsc1_redundancy)
    rsc1 = RSCodec(rsc1_redundancy, nsize=255)
    rsc2 = RSCodec(rsc2_redundancy, nsize=255)
    word = bytearray(word) + bytearray(8 * int(m*gamma_tag))  # allocation
    for i, v in enumerate(vertices):  # encode each node twice
        word[m+nodeword_length*i:m+nodeword_length*(i+1)] = rsc2.encode(rsc1.encode(v)[d:])
    return word


def decode_ramanujan(graph, codeword, gamma_tag):
    """
    This function decodes the redundancies of codeword with rate 1/4 Reed Solomon
    and then decodes each of the vertices with systematic MDS.
    :param graph: Ramanujan graph
    :param codeword: word to decode - a list of size 2 - the word and a list of redundancies
    :param gamma_tag: the rate of the first Reed Solomon??
    :return: the decoded word
    """
    # graph stuff
    num_of_nodes = graph.num_of_nodes
    d = graph.degree

    # extract from the encoding
    word = bytearray(codeword[0])  # the original word
    check_symbols = codeword[1]  # the encoded redundancy for each node

    # setting up the reed solomon
    redundancy = round(4 * d * gamma_tag)
    rsc1_redundancy = round(gamma_tag*d + 0.5)
    rsc2_redundancy = int(redundancy - rsc1_redundancy)
    rsc1 = RSCodec(rsc1_redundancy, nsize=255)
    rsc2 = RSCodec(rsc2_redundancy, nsize=255)

    finished = [False] * num_of_nodes  # for each node we need to know if it finished
    success_flag = True  # we return a flag that indicates if we think we decoded successfully
    # decode each of the check symbols
    for i_cs, cs in enumerate(check_symbols):
        to_dec = cs
        try:
            check_symbols[i_cs] = list(rsc2.decode(to_dec)[0])
        except reedsolo.ReedSolomonError:
            success_flag = False  # we failed a decoding, so we think we failed
            finished[i_cs] = True  # the check symbols are wrong, and we don't want to continue decoding with it

    left_to_decode = LinkedList(graph.A)  # the linked list we run over in the main loop

    edges = list(graph.edges())  # the edges of the graph
    Ev = [[-1] * d for _ in range(num_of_nodes)]  # edges connected to v
    symbol_counters = [0] * num_of_nodes
    for i, (node1, node2) in enumerate(edges):
        vertex_index = symbol_counters[node1]
        Ev[node1][vertex_index] = i  # append the index to the first node list
        vertex_index = symbol_counters[node2]
        Ev[node2][vertex_index] = i  # append the index to the second node list
        symbol_counters[node1] += 1  # increment the first counter
        symbol_counters[node2] += 1  # increment the second counter

    is_in_linked_list = [False] * num_of_nodes  # list to make sure there are no duplicates in the linked list
    first_time = True  # if it is first time, we want to run over all B side and not just the neighbors
    while left_to_decode.head:  # while there are still nodes in the linked list
        temp_linked_list = LinkedList()
        for x in left_to_decode.run_over():  # run over the nodes in the current linked list
            is_in_linked_list[x] = False  # reset it for the next iteration to be able to append us
            if finished[x]:  # if we already decoded the node continue to the next one
                continue
            word_v = [word[j2] for j2 in Ev[x]]  # symbols on the edges of v
            redundancy_v = check_symbols[x]  # the redundancy of v
            try:
                rmes, rmesecc, errata_pos = rsc1.decode(word_v + redundancy_v)
            except reedsolo.ReedSolomonError:
                continue
            if errata_pos and errata_pos[0] >= d:  # check if the redundancy is correct
                continue
            # copying the decoded symbols
            for i, symbol in zip(Ev[x], rmes):
                word[i] = symbol
            finished[x] = True  # set the node as decoded
            # create a linked list of only the neighbors that aren't already in it
            to_append = [j for j in graph.neighbors[x] if not is_in_linked_list[j]]
            temp_linked_list.insert_list(to_append)
        if not first_time:
            left_to_decode = temp_linked_list
        else:
            left_to_decode = LinkedList(graph.B)  # linked list of B side
        first_time = False
    return word, (min(finished) and success_flag)  # the word and a flag if we think we finished
