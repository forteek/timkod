import math
import glob
from collections import Counter
import struct
import json


def count_element_occurrences(elements):
    element_counts = Counter(elements)

    return {key: value for key, value in element_counts.items()}


def generate_code(elements_probabilities):
    elements_probabilities = {k: v for k, v in sorted(elements_probabilities.items(), key=lambda item: item[1], reverse=True)}

    codebook = {}
    current_code = 0
    bit_length = (len(elements_probabilities) - 1).bit_length()
    for element in elements_probabilities:
        codebook[element] = f'{current_code:0{bit_length}b}'
        current_code += 1

    return codebook


def encode(text, codebook):
    encoded_bitstring = ''.join(codebook[char] for char in text)
    encoded_bitstring += '0' * (8 - len(encoded_bitstring) % 8)

    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bitstring), 8):
        encoded_bytes.append(int(encoded_bitstring[i:i + 8], 2))

    return bytes(encoded_bytes)


def decode(encoded_bytes, codebook):
    decoded_bitstring = ''
    for byte in encoded_bytes:
        decoded_bitstring += f'{byte:08b}'

    decoded_bitstring = decoded_bitstring.rstrip('0')
    codebook = {v: k for k, v in codebook.items()}
    char_length = len(list(codebook.keys())[0])

    decoded_text = ''
    for i in range(0, len(decoded_bitstring), char_length):
        if len(decoded_bitstring[i:i+char_length]) != char_length:
            decoded_text += codebook[decoded_bitstring[i:].ljust(char_length, '0')]
            continue

        decoded_text += codebook[decoded_bitstring[i:i+char_length]]

    return decoded_text


if __name__ == '__main__':
    with open('plik', 'r') as file:
        text = file.read()

    letters_occurrences = count_element_occurrences(text)
    codebook = generate_code(letters_occurrences)

    encoded_text = encode(text, codebook)
    with open('plik.bin', 'wb') as file:
        file.write(encoded_text)
    with open('plik.cb', 'w') as file:
        file.write(json.dumps(codebook))

    # with open('plik.bin', 'rb') as file:
    #     text = file.read()
    # with open('plik.cb', 'r') as file:
    #     codebook = json.loads(file.read())
    #
    # decoded_text = decode(text, codebook)
    # print(decoded_text)
