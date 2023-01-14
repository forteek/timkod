import math


def encode(text, max_codebook_length = 2 ** 12):
    code = {(i,): i for i in range(256)}
    last_code = 256

    result = []
    text = [char for char in text]

    left_side = (text[0],)
    for right_side in text[1:]:
        both_sides = (*left_side, right_side)
        if both_sides in code:
            left_side = both_sides
        else:
            if last_code >= max_codebook_length:
                result.append(code[left_side])
                left_side = (right_side,)

                continue

            result.append(code[left_side])
            code[both_sides] = last_code
            last_code += 1
            left_side = (right_side,)

    result.append(code[left_side])

    length = math.ceil(math.log2(last_code))
    fixed_length_codebook = {v: f'{v:0{length}b}' for k, v in code.items()}

    encoded_bitstring = ''.join(fixed_length_codebook[char] for char in result)
    encoded_bitstring += '0' * (8 - len(encoded_bitstring) % 8)

    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bitstring), 8):
        encoded_bytes.append(int(encoded_bitstring[i:i + 8], 2))

    # reversed_codebook = {v: k for k, v in codebook.items()}
    # print(reversed_codebook)
    # print(flatten([reversed_codebook[x] for x in result]))

    return bytes(encoded_bytes), length


def decode(encoded_bytes, code_length):
    code = {i: chr(i) for i in range(256)}
    last_code = 256
    decoded_bitstring = ''.join(f'{byte:08b}' for byte in encoded_bytes)

    result = bytearray()
    carry = ''

    char_length = code_length

    chunks = [int(decoded_bitstring[i:i+char_length], 2) for i in range(0, len(decoded_bitstring), char_length)]
    old = chunks.pop(0)
    result.append(ord(code[old]))

    for chunk in chunks:
        if chunk in code:
            word = code[chunk]
        else:
            word = code[old] + carry

        for char in word:
            result.append(ord(char))
        carry = word[0]

        if last_code >= max_codebook_length:
            old = chunk
            continue

        code[last_code] = code[old] + carry
        last_code += 1
        old = chunk

    # print(code)

    return result

def flatten(list):
    items = []
    for item in list:
        if type(item) is list or type(item) is tuple:
            items.extend(flatten(item))
        else:
            items.append(item)
    return items


def tuples_to_string(tuples, reverse_codebook):
    result = []
    for char in tuples:
        if type(char) is tuple:
            result.extend(tuples_to_string(char, reverse_codebook))
        else:
            result.append(reverse_codebook[char])
    return result


if __name__ == '__main__':
    files = ['wiki_sample.txt', 'norm_wiki_sample.txt', 'lena.bmp']
    for file in files:
        print('zaczynam plik ' + file)
        filename, extension = file.split('.')
        max_codebook_lengths = {'xx': 2 ** 128}
        for variant, max_codebook_length in max_codebook_lengths.items():
            print('zaczynam wariant ' + variant)
            with open(f'input/{filename}.{extension}', 'rb') as file:
                text = file.read()

            encoded_text, code_length = encode(text, max_codebook_length)
            print('dugosc mi wyszla ', code_length)

            with open(f'output/{filename}.{variant}.bin', 'wb') as file:
                file.write(encoded_text)

            with open(f'output/{filename}.{variant}.bin', 'rb') as file:
                text = file.read()

            decoded_text = decode(text, code_length)
            with open(f'proof/{filename}.{variant}.{extension}', 'wb') as file:
                file.write(decoded_text)
