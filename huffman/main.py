from collections import Counter
import json


def count_element_occurrences(elements):
    element_counts = Counter(elements)

    return {key: value for key, value in element_counts.items()}


def generate_code(elements_probabilities):
    elements_probabilities = {k: v for k, v in sorted(elements_probabilities.items(), key=lambda item: item[1], reverse=True)}

    elements = []
    for letter, occurrences in elements_probabilities.items():
        elements.append({
            'letter': letter,
            'occurrences': occurrences,
            'left': None,
            'right': None
        })

    while len(elements) > 1:
        elements = sorted(elements, key=lambda element: element['occurrences'])
        left = elements.pop(0)
        right = elements.pop(0)

        elements.append({
            'letter': None,
            'occurrences': left['occurrences'] + right['occurrences'],
            'left': left,
            'right': right
        })

    codebook = {}
    root = elements.pop(0)
    codebook_builder(root, '', codebook)

    return codebook

def codebook_builder(element, code, codebook):
    if element['letter'] is not None:
        codebook[element['letter']] = code
        return

    codebook_builder(element['left'], code + '0', codebook)
    codebook_builder(element['right'], code + '1', codebook)


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

    codebook = {v: k for k, v in codebook.items()}

    decoded_text = ''
    while decoded_bitstring:
        i = 1
        while decoded_bitstring[:i] not in codebook:
            i += 1

        if codebook[decoded_bitstring[:i]] == "\x00":
            break

        decoded_text += codebook[decoded_bitstring[:i]]
        decoded_bitstring = decoded_bitstring[i:]

    return decoded_text


if __name__ == '__main__':
    with open('plik', 'r') as file:
        text = file.read()

    text += "\x00"

    letters_occurrences = count_element_occurrences(text)
    codebook = generate_code(letters_occurrences)
    # print(codebook)

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
