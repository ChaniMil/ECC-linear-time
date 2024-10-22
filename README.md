# LTCode

## Description
This project implements a fast error-correcting code according to the article "Linear-Time Encodable/Decodable Codes With Near-Optimal Rate".\
The code can correct a fraction e of errors and a fraction s of erasures, if 2e+s ≤ 1-r-ε, 
where r is the code rate and ε is a small value.\
It provides encoding and decoding functions, with flexability on the parameters set.\
The minimum size of a word to encode is about 80,000 bytes.\
You can encode bytes, bytearray, an integer list in range [0, 255], and a bin file.

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

First, you need to create an object of LTCode.\
It has three inputs `LTCode(epsilon, r, k)`:
- epsilon - the distance from optimal MDS code
- r - code rate
- k - code dimension (message length)


#### Encoding
To encode, use `encode(data, output_path)`
- data - two options:\
        1. The message to encode, which must be in the form of bytes, bytearray or list\
        2. A path to a bin file, as a string, pointing to the data
- output_path - (optional) The file path where the encoded codeword will be stored
Examples of use:
```bash
# Initialization
# create an object that encodes messages of length 4, and has r≈0.7 and epsilon≈0.2.
>>> from LT_code import LTCode
>>> ltc = LTCode(0.2, 0.7, k=4)  # r≈0.7, epsilon≈0.2

# Encoding
# encoding a list of symbols:
>>> ltc.encode([1,2,3,4])
[[1, 0, ..., 0, 0], [0, 0, ..., 0, 0], ..., [0, 0, ..., 0, 0], [0, 0, ..., 0, 0]]

# encoding a bytearray
>>> ltc.encode(bytearray([1,2,3,4]))
[[1, 0, ..., 0, 0], [0, 0, ..., 0, 0], ..., [0, 0, ..., 0, 0], [0, 0, ..., 0, 0]]

# encoding a byte string
>>> ltc = LTCode(0.2, 0.7, 11)
>>> codeword = ltc.encode(b'hello world')
>>> print(codeword)
[[104, 0, ..., 0, 0], [0, 0, ..., 0, 0], ..., [0, 0, ..., 0, 0], [0, 0, ..., 0, 0]]

# encoding using a file
>>> ltc.encode('message.bin', output_path='codeword.bin')
[[100, 0, ..., 0, 0], [0, 0, ..., 0, 0], ..., [0, 0, ..., 0, 0], [0, 0, ..., 0, 0]]
```

#### Decoding
To decode, use `decode(data, output_path)`
- data - two options:\
        1. The message to decode, of the codeword type: list of lists\
        2. A path to a bin file, as a string, pointing to the data
- output_path - (optional) The file path where the decoded word will be stored
The function returns the decoded message and a flag that indicates whether the program considers the decoding successful.\
\
Examples of use:
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

# decode with 5 errors
>>> codeword[:10] = [[1] * delta] * 10
>>> ltc.decode(codeword)
(bytearray(b'hello world'), True)

# decoding using a file
>>> ltc.decode('codeword.bin', output_path='original.bin')
(bytearray(b'dolev chani'), True)
```
#### Decoding with Erasures
To manage erasures, you can assign `erase_pos` a list containing the indices of the erasures in the `decode()` input.
```bash
# Erasures
# decode 10 erasures:
>>> codeword[:20] = [[ord('-')] * delta] * 20
>>> ltc.decode(codeword, erase_pos=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19])
(bytearray(b'hello world'), True)

```
#### Parameters
To choose parameters according to your preferences from a list, you can use `get_params_list(eps_dist, r_dist, prime_limit, max_k)`.
- eps_dist - the distance from your given epsilon you allow us to choose the code's epsilon 
- r_dist - the distance from your given r you allow us to choose the code's r 
- prime_limit - the upper bound of prime numbers for the graphs.
- k_max - the upper bound of the code dimension.
Note: these 4 parameters can also be used in `encode()`, `decode()` and `LTCode()`.\
To choose the parameter set from the list use `choose_index(index)`.
```bash
>>> ltc = LTCode(0.2, 0.7)
>>> params_list = get_params_list(eps_dist=0.2, r_dist=0.2)
>>> print(len(params_list))
7
>>> ltc.choose_index(3)
(137, 53, 181, 53, 146, 0.7582417582417582, 0.2318840579710145, 10268856)

```
The parameters for the code are (pr, qr, pe, qe, b, r, epsilon, k) \
The graphs are generated according to the linear time deterministic construction as described in the article 'Ramanujan Graphs'.
- pr, qr - 2 primes used to generate the ramanujan graph
- pe, qe - 2 primes used to generate the expander graph
To get a deeper understanding of the parameters, you can read the 'Parameters' section in the file project_book.pdf.

#### Error-correction capability
To get the maximum fraction of errors or erasures that can be independently corrected, call `decoding_capability()` with no inputs.\
To get the maximum fraction of errors and erasures that can be simultaneously corrected, specify the fraction of errors or erasures you expect.\
the output of the function is `(max_errors, max_erasures)`
```bash
>>> ltc.decoding_capability()
(0.014545454545454486, 0.029090909090908973)

>>> fraction = (1-r-epsilon)/3

>>> ltc.decoding_capability(erasures=fraction)
(0.009696969696969659 0.009696969696969657)

>>> ltc.decoding_capability(errors=fraction)
(0.009696969696969657 0.009696969696969659)
```
### low level
If you want full control, you can skip th API and directly use the library as-is:
#### Parameters
First you need to generate parameters for the code, you can use one of the functions that appear in the parameters.py file, or create your own function.
```bash
>>> import parameters
>>> params = parameters.choose_params(0.7,0.2)
>>> print(params[0])
(137, 29, 193, 29, 146, 0.7113402061855669, 0.2318840579710145, 1680840)
# the parameters in order are (pr, qr, pe, qe, b, r, epsilon, k)
```
#### Graphs
If you encode more than one message, you can create the ramanujan graph and the expander graph before the encoding.\
If you don't create the graphs before the encoding or decoding, they will be generated in the functions.
```bash
>>> import main_code
>>> pr, qr, pe, qe = params[:4]
>>> ramanujan, expander = main_code.init_graphs(pr, qr, pe, qe)
```
#### Encoding
To encode a word, use the function `linear_encode(message_to_encode, pr, qr, pe, qe, b, epsilon, ramanujan_graph, expander_graph)`:
- message_to_encode - the message to be encoded
- pr, qr, pe, qe - the primes of the graphs
- b - the size of each block before Reed-Solomon encoding
- epsilon - small value related to the distance of the code
- ramanujan_graph, expander_graph - (optional) the graphs generated before the encoding
To get a deeper understanding of the parameters, you can read the 'Parameters' section in the file project_book.pdf.


```bash
>>> word = b'LinearTime'*168084
>>> codeword = main_code.linear_encode(word, *params[:5], params[6], ramanujan, expander)
>>> print(codeword)
[[76, 76, ..., 38, 91], [76, 97, ..., 48, 192], ..., [167, 24, ..., 246, 242], [42, 51, ..., 180, 153]]
```
#### Decoding
To decode, use the function linear_decode:
- message_to_encode - the codeword to be decoded
- pr, qr, pe, qe - the primes of the graphs
- b - the size of each block after Reed-Solomon decoding
- epsilon - small value related to the distance of the code
- ramanujan_graph, expander_graph - (optional) the graphs generated before the encoding
- erase_pos - list of indices where an erasure occured
To get a deeper understanding of the parameters, you can read the 'Parameters' section in the file project_book.pdf.


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

