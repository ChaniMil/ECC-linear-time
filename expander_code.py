from LinkedList import LinkedList


def encode_expander(graph, blocks):
    """
    This function sends the data from the left side of the bipartite graph to the right
    :param graph: expander Ramanujan graph
    :param blocks: data to encode, each block is sent via one node
    :return: encoded data (changes the order of blocks)
    """
    # graph info
    delta = graph.degree  # graph is delta regular
    n = graph.num_of_nodes
    left, right = graph.sets

    mid_codeword = [[0] * delta for _ in range(n)]  # initializing the n new symbols
    counters = [0] * n  # the next empty slot on each symbol

    # goes through the left nodes, and saves the data in the order of the graph
    for i in range(n // 2):
        neighbors_of_i = sorted(graph.neighbors[left[i]])
        for j in range(delta):
            k = counters[neighbors_of_i[j]]  # the next empty slot in the block on the left side
            mid_codeword[neighbors_of_i[j]][k] = blocks[i][j]  # transmitting the symbol
            counters[neighbors_of_i[j]] += 1

    # take only the left nodes
    final_codeword = [mid_codeword[r] for r in right]
    return final_codeword


def decode_expander(graph, new_symbols, erasures):
    """
    This function sends the data from the right side of the bipartite graph to the left
    :param graph: expander Ramanujan graph
    :param new_symbols: data to decode, each block is sent via one node
    :param erasures: a list of indices to what symbols are erased
    :return: decoded data (changes the order of blocks)
    """
    # graph info
    delta = graph.degree  # graph is delta regular
    n = graph.num_of_nodes
    left, right = graph.sets

    # a simpler way to check if an erasure occurred, boolean masking
    boolean_erasures = [False] * (n // 2)
    for s in erasures:
        boolean_erasures[s] = True

    new_erasures = [LinkedList() for _ in range(n)]  # for each node to create a linked list for its erasures
    blocks = [[0] * delta for _ in range(n)]  # initialize the blocks to return
    counters = [0] * n  # counts how many symbols in left side has been updated, holds the next empty slot in the block

    # goes through the right nodes, and saves the data in the order of the graph
    for i in range(n // 2):  # run over all elements on the right size
        neighbors_of_i = sorted(graph.neighbors[right[i]])
        for j in range(delta):
            k = counters[neighbors_of_i[j]]  # the next empty slot in the block on the left side
            blocks[neighbors_of_i[j]][k] = new_symbols[i][j]  # transmitting the symbol
            counters[neighbors_of_i[j]] += 1
            # if an erasure occurred in the right symbol, set the symbol on the left as an erasure
            if boolean_erasures[i]:
                new_erasures[neighbors_of_i[j]].insertAtBegin(k)

    # take only the left nodes
    original_word = [blocks[l] for l in left]
    list_new_erasures = [list(new_erasures[left[i]].run_over()) for i in range(n // 2)]
    return original_word, list_new_erasures
