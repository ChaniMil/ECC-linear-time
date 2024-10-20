# LTCode

## Description
This project implements a fast error-correcting code according to the article "Linear-Time Encodable/Decodable Codes With Near-Optimal Rate".\
It provides encoding and decoding functions, with flexability on the parameters set.\
The minimum size of a word to encode is about 80,000 bytes.\
You can encode bytes, bytearray, and an integer array in range [0, 255].

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [high level](#high-level)
  - [low level](#low-level)
- [Authors](#authors)
- [License](#license)

## Installation
1. Clone the repository: `git clone https://github.com/ChaniMil/ECC-linear-time`
2. Navigate to the project directory: `cd ECC-linear-time`
3. Install dependencies: `pip install -r requirements.txt`

## Usage
### high level

```bash
# Initialization
# chooses the smallest k we can encode with
>>> from LT_code import LTCode
>>> ltc = LTCode(0.2, 0.7, k=4, epsilon_dist=0.1, r_dist=0.1)  # r≈0.7, epsilon≈0.2

# Encoding
# encoding a list of symbols:
>>> ltc.encode([1,2,3,4])
[[1, 0, ..., 0, 0], [0, 0, ..., 0, 0], ..., [0, 0, ..., 0, 0], [0, 0, ..., 0, 0]]

# encoding bytearray
>>> ltc.encode(bytearray([1,2,3,4]))
[[1, 0, ..., 0, 0], [0, 0, ..., 0, 0], ..., [0, 0, ..., 0, 0], [0, 0, ..., 0, 0]]

# encoding a byte string
>>> ltc = LTCode(0.2, 0.7, 11)
>>> codeword = ltc.encode(b'hello world')
>>> print(codeword)
[[104, 0, ..., 0, 0], [0, 0, ..., 0, 0], ..., [0, 0, ..., 0, 0], [0, 0, ..., 0, 0]]
```
Note: the encoding and decoding of LTCode depends on the code dimension - k, you need to choose the right size.


```bash
# Decoding (repairing)
# shape of the codeword and r and epsilon
>>> delta = len(codeword[0])
>>> n = len(codeword)
>>> r = ltc.params[5]
>>> epsilon = ltc.params[6]

# decoding with 0 errors
>>> ltc.decode(codeword) # original
(bytearray(b'hello world'), True)

# decode with fraction of (1-r-epsilon)/2 errors
>>> fraction = (1-r-epsilon)/2
>>> codword[:int(fraction*n)] = [[0] * delta] * int(fraction*n)
>>> ltc.decode(codeword)
(bytearray(b'hello world'), True)
```

Note: with the decoded message, we also receive a flag that indicates whether the program thinks the decoding was successful.

```bash
# Erasures
# for erasures we need to input the function with the list of the indices.
# decode a fraction of 1-r-epsilon erasures:
>>> fraction = 1-r-epsilon
>>> codeword[:int(fraction*n)] = [[ord('-')] * delta] * int(fraction*n)
>>> ltc.decode(codeword, erase_pos=list(range(int(fraction*n))))
(bytearray(b'hello world'), True)

```
For the choosing of the parameters, if you want to get a list and choose parameters as you wish, you can do so by using get_k_list.
```bash
>>> ltc = LTCode(0.2, 0.7)
>>> params_list = get_k_list(e_close=0.2, r_close=0.2)
>>> print(len(params_list))
7
>>> ltc.choose_index(3)
(137, 53, 181, 53, 146, 0.7582417582417582, 0.2318840579710145, 10268856)

```


To get the maximum number of errors and erasures that can be simultaneously corrected, you need to specify the number of errors or erasures you expect:

```bash
>>> fraction = (1-r-epsilon)/3

>>> maxerrors, maxerasures = ltc.decoding_capability(erasures=fraction)
>>> print(maxerrors, maxerasures)
0.009696969696969659 0.009696969696969657

>>> maxerrors, maxerasures = ltc.decoding_capability(errors=fraction)
>>> print(maxerrors, maxerasures)
0.009696969696969657 0.009696969696969659
```
### low level
If you want full control, you can skip th API and directly use the library as-is:\
First you need to generate params for the code, you can use the choose_params function, and create the ramanujan graph and the expander graph.
```bash
>>> import parameters
>>> import main_code
>>> params = parameters.choose_params(0.7,0.2)[0]
>>> print(params)
(137, 29, 193, 29, 146, 0.7113402061855669, 0.2318840579710145, 1680840)
# there are 7 parameters, we chose the first one
# the parameters in order are (pr, qr, pe, qe, b, r, epsilon, k)

# receives pr,qr,pe,qe and creates corresponding graphs
>>> ramanujan, expander = main_code.init_graphs(*params[:4])
```
then, to encode a word we use the function linear_encode:
```bash
>>> word = b'LinearTime'*168084
>>> codeword = main_code.linear_encode(word, *params[:5], params[6], ramanujan, expander)
>>> print(codeword)
[[76, 76, ..., 38, 91], [76, 97, ..., 48, 192], ..., [167, 24, ..., 246, 242], [42, 51, ..., 180, 153]]
```
to decode we can simply use the linear_decode function:
```bash
>>> codeword[0] = [0] * (params[2]+1)
>>> main_code.linear_decode(codeword, *params[:5], params[6], ramanujan, expander, erasures=[1, 2])
(bytearray(b'LinearTimeLinearTimeLinearTime...LinearTimeLinearTime'), True)
```

## Authors
We are Dolev Shmaryahu and Chani Milshtein, computer engineering students at Bar-Ilan University. This is our final project for our engineering degree.


## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software in accordance with the terms of the license.

For more details, see the [LICENSE](./LICENSE) file.

