import math
import glob
from collections import Counter
import struct
import json


def encode(text, max_codebook_length = 2 ** 12):
    codebook = {(i,): i for i in range(256)}
    last_code = 256

    result = []
    text = [ord(char) for char in text]

    left_side = (text[0],)
    for right_side in text[1:]:
        both_sides = (*left_side, right_side)
        if both_sides in codebook:
            left_side = both_sides
        else:
            if last_code >= max_codebook_length:
                result.append(codebook[left_side])
                left_side = (right_side,)

                continue

            result.append(codebook[left_side])
            codebook[both_sides] = last_code
            last_code += 1
            left_side = (right_side,)

    result.append(codebook[left_side])

    length = math.ceil(math.log2(max_codebook_length))
    fixed_length_codebook = {v: f'{v:0{length}b}' for k, v in codebook.items()}

    encoded_bitstring = ''.join(fixed_length_codebook[char] for char in result)
    encoded_bitstring += '0' * (8 - len(encoded_bitstring) % 8)

    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bitstring), 8):
        encoded_bytes.append(int(encoded_bitstring[i:i + 8], 2))

    reverse_codebook = {v: k for k, v in codebook.items()}

    return bytes(encoded_bytes), codebook


def decode(encoded_bytes, max_codebook_length = 2 ** 12):
    codebook = {(i,): i for i in range(256)}
    reverse_codebook = {v: k for k, v in codebook.items()}
    char_length = math.ceil(math.log2(max_codebook_length))

    decoded_bitstring = ''
    for byte in encoded_bytes:
        decoded_bitstring += f'{byte:08b}'

    decoded_bitstring = decoded_bitstring.rstrip('0')

    result = []
    carry = None
    last_code = 256
    old = (int(decoded_bitstring[:char_length], 2),)
    result.append(codebook[old])

    for i in range(char_length, len(decoded_bitstring), char_length):
        if len(decoded_bitstring[i:i+char_length]) != char_length:
            new = (int(decoded_bitstring[i:i+char_length].ljust(char_length, '0'), 2),)
        else:
            new = (int(decoded_bitstring[i:i+char_length], 2),)

        if new in codebook:
            word = new
            word_literal = (codebook[word],)
        else:
            if carry is not None:
                word = (*old, carry)
                word_literal = reverse_codebook[new[0]]
            else:
                word = old
                word_literal = (codebook[word],)

        for char in word_literal:
            result.append(char)
        carry = word_literal[0]

        if last_code >= max_codebook_length:
            old = new
            continue

        codebook[(*old, carry)] = last_code
        reverse_codebook[last_code] = (*old, carry)
        last_code += 1
        old = new

    return ''.join([chr(x) for x in result])


if __name__ == '__main__':
    # with open('lena.bmp', 'rb') as file:
    #     text = file.read()
    text = 'zazolc gesla jazn, kocham jesc placki. placek to ja jestem.'

    max_codebook_length = 2 ** 12

    encoded_text, codebook = encode(text, max_codebook_length)

    with open('plik.bin', 'wb') as file:
        file.write(encoded_text)

    with open('plik.bin', 'rb') as file:
        text = file.read()

    decoded_text = decode(text, max_codebook_length)
    with open('plik.bmp', 'w') as file:
        file.write(decoded_text)
    print(decoded_text)
