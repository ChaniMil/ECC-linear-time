import galois
from Graph import Graph
from parameters import check_legendre_symbols


def generate_elements(p):
    """
    this function collects all the elements of length 4,
    such that their square sum is p,
    a0 is odd and positive, and a1,a2,a3 are even.
    :param p: a prime
    :return: the list of elements
    """
    elements = []
    squared = [0, 0, 0, 0]
    sqrt_p = int(p ** (1 / 2))
    sqrt_p_even = sqrt_p // 2 * 2
    sqrt_p_odd = sqrt_p_even + 1
    for a_0 in range(1, sqrt_p_odd + 1, 2):
        squared[0] = (a_0 * a_0)
        for a_1 in range(-sqrt_p_even, sqrt_p_even + 1, 2):
            squared[1] = (a_1 * a_1)
            for a_2 in range(-sqrt_p_even, sqrt_p_even + 1, 2):
                squared[2] = (a_2 * a_2)
                for a_3 in range(-sqrt_p_even, sqrt_p_even + 1, 2):
                    squared[3] = (a_3 * a_3)
                    if sum(squared) == p:
                        elements.append([a_0, a_1, a_2, a_3])
    return elements


def matrix_multiply(a, b, mult, q):
    """
    this function calculates the multiplication of matrices
    :param a: first matrix
    :param b: second matrix
    :param mult: LUT which contains all the multiplications of the field GF(q)
    :param q: the size of the field
    :return: the multiplication of the two matrices
    """
    c = [mult[a[0]][b[0]]+mult[a[1]][b[2]], mult[a[0]][b[1]]+mult[a[1]][b[3]],
         mult[a[2]][b[0]]+mult[a[3]][b[2]], mult[a[2]][b[1]]+mult[a[3]][b[3]]]
    if c[0] >= q:
        c[0] -= q
    if c[1] >= q:
        c[1] -= q
    if c[2] >= q:
        c[2] -= q
    if c[3] >= q:
        c[3] -= q
    return c


def PGL(q, mult):
    """
    this function runs over all the representatives of the elements of the group PGL
    :param q: the size of the field
    :param mult: 2d list containing all the multiplications
    :return: all the representatives of the elements of this group
    """
    for y2 in range(q):
        for y3 in range(1, q):
            yield 0, 1, y3, y2
            prod = mult[y2][y3]
            for y4 in range(q):
                if y4 != prod:
                    yield 1, y2, y3, y4
        for y4 in range(1, q):
            yield 1, y2, 0, y4


def matrix_to_int(a1, a2, a3, a4, q):
    """
    this function computes a mapping of a matrix to an integer
    :param a1: first element of the matrix
    :param a2: second element of the matrix
    :param a3: third element of the matrix
    :param a4: fourth element of the matrix
    :param q: the size of the elements' field
    :return: the representation of the matrix as an integer
    """
    if a1 == 0:
        return a4*(q-1) + (a3-1)
    else:
        return a2*q*q + a3*q + a4 + (q*q-q)
    # (q-1)qq+(q-1)q+q-1+q(q-1)
    # q^3+q^2-q-1=(q+1)^2(q-1)


def generate_cayley_graph(elements, GF, q, p):
    """
    this function builds a cayley graph using the group PGL
    :param elements: the list of elements we generated in the 'generate_elements' function with input p
    :param GF: Galois field of size q
    :param q: the amount of nodes is q(q-1)(q+1), and the matrices are of the field GF(q)
    :param p: the degree of the graph minus 1
    :return: the graph we built
    """
    G = Graph(q * (q * q - 1), p + 1)
    inv = [0] + [int(GF(1)/GF(a)) for a in range(1, q)]
    mult = [[int(GF(i)*GF(j)) for j in range(q)] for i in range(q)]
    real_indices = [0] * ((q+1)*(q+1)*(q-1) + 1)
    for i, matrix in enumerate(PGL(q, mult)):
        real_indices[matrix_to_int(*matrix, q)] = i
    quad_res = [False] * q
    for i in range(1, q):
        quad_res[mult[i][i]] = True
    for y in PGL(q, mult):
        det = mult[y[3]][y[0]]-mult[y[1]][y[2]]
        if det < 0:
            det += q
        if quad_res[det]:
            continue
        y_int = real_indices[matrix_to_int(*y, q)]
        for s in elements:
            x = matrix_multiply(s, y, mult, q)
            if x[0] == 0:
                x_int = real_indices[matrix_to_int(0, 1, mult[x[2]][inv[x[1]]], mult[x[3]][inv[x[1]]], q)]
            else:
                x_int = real_indices[matrix_to_int(1, mult[x[1]][inv[x[0]]], mult[x[2]][inv[x[0]]], mult[x[3]][inv[x[0]]], q)]
            G.add_edge(x_int, y_int, quad_res[det])
    return G


def find_i(q):
    """
    this function finds an element 'i' in the field GF(q) such that i^2=-1
    :param q: the size of the field
    :return: the element we found
    """
    for j in range(q):
        if pow(j, 2, q) == q - 1:
            return j


def is_right_size(graph):
    if len(set([x for x in graph.neighbors[0]])) != graph.degree:
        raise ValueError("Failed to create the Ramanujan graph")


def find_S(i, p, q):
    elements = generate_elements(p)
    return [((a0 + i * a1) % q, (a2 + i * a3) % q, (-a2 + i * a3) % q, (a0 - i * a1) % q) for [a0, a1, a2, a3] in
            elements]


def ramanujan(p, q):
    """
    this function is the main function we call when we want a graph
    :param p: it tells the degree of the graph p+1
    :param q: it tells the number of nodes in the graph q(q+1)(q-1)
    :return: a ramanujan graph
    """
    if not check_legendre_symbols(p, q):
        raise "Error: The legendre symbol isn't -1"
    GF = galois.GF(q)
    i = find_i(q)
    matrices = find_S(i, p, q)
    G = generate_cayley_graph(matrices, GF, q, p)
    G.split_to_sides()
    is_right_size(G)
    return G
