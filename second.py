import os
import math
import bitarray


def count_chars(text):
    char_counts = {}

    for char in text:
        if char in char_counts:
            char_counts[char] += 1
        else:
            char_counts[char] = 1

    return char_counts


def bits(value, length):
    bits = format(value, 'b')
    bits = bits.zfill(length)

    return bits


def create_code(chars):
    code = {}
    char_count = len(chars.keys())
    length = math.ceil(math.log(char_count + 1, 2))

    for index, key in enumerate(chars.keys()):
        char_representation = bits(index, length)
        code[key] = char_representation

    return code


def encode(code, text):
    encoded = bits(0, 0)

    for char in text:
        encoded += code[char]

    return encoded


def decode(text, code, length):
    decoded_text = ''
    num_codes = len(text)

    for i in range(num_codes):
        char_representation = text[i * length: (i + 1) * length]
        decoded_text += code[char_representation] if char_representation in code else ''

    return decoded_text


def save(code, encoded):
    with open('key', 'w') as key_file:
        key_file.write(''.join(code.keys()))

    encoded += ''.join(['1' for _ in range(8 - len(encoded) % 8)])
    with open('encoded', 'wb') as encoded_file:
        encoded_file.write(bitarray.bitarray(encoded).tobytes())

def load():
    with open('encoded', 'rb') as encoded_file:
        encoded = bitarray.bitarray()
        encoded.fromfile(encoded_file)
        encoded = encoded.to01()

    with open('key', 'r') as key_file:
        key = key_file.read()
        length = math.ceil(math.log(len(key) + 1, 2))

    code = {}
    for index, char_representation in enumerate(key):
        char = bits(index, length)
        code[char] = char_representation

    return encoded, code, length


def calculate_sizes(directory, original):
    encoded_size = os.stat(directory + 'encoded_result').st_size
    key_size = os.stat(directory + 'key').st_size
    original_size = os.stat(original).st_size
    return encoded_size, key_size, original_size


if __name__ == '__main__':
    with open('plik', 'r') as file:
        content = file.read()

    chars = count_chars(content)
    code = create_code(chars)

    encoded = encode(code, content)
    save(code, encoded)

    encoded, code, length = load()
    decoded = decode(encoded, code, length)


    # letters_dictionary = analyze_content(content)
    # code_dict, code_length = create(letters_dictionary)
    # encoded = encode(code_dict, content)
    # save(code_dict, encoded, directory_name)
    # encoded_content, loaded_code_length, loaded_code_dictionary = load(directory_name)
    # decoded = decode(encoded_content, loaded_code_dictionary, loaded_code_length)
    # en_size, k_size, o_size = calculate_sizes(directory_name, file_name)
    #
    # sum_size = k_size + en_size
    # print('Original file => ' + file_name)
    # print('Size          => ' + str(o_size) + ' [bytes]')
    #
    # print('Encoded size:')
    # print('\tEncoded   => ' + str(en_size) + ' [bytes]')
    # print('\tKey       => ' + str(k_size) + ' [bytes]')
    # print('\tSUM       => ' + str(sum_size) + ' [bytes]')
    #
    # print('Compare files')
    # if decoded == content:
    #     print('\tEquality correct ✓')
    #     print('\tCompression Ratio => ' + str(o_size / sum_size))
    #     print('\tSpace savings     => ' + str(1 - sum_size / o_size))
    # else:
    #     print('\tContent =/= Decoded(Encoded(Content))')
    #
    #     print(content)
    #     print('\n\n--------\n\n')
    #     print(decoded)
