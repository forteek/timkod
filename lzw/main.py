import math


def encode(text, max_codebook_length = 2 ** 12):
    codebook = {(i,): i for i in range(256)}
    last_code = 256

    result = []
    text = [char for char in text]

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

    # reversed_codebook = {v: k for k, v in codebook.items()}
    # print(reversed_codebook)
    # print(flatten([reversed_codebook[x] for x in result]))

    return bytes(encoded_bytes), codebook


def decode_letters(encoded_bytes, max_codebook_length = 2 ** 12):
    code = {i: chr(i) for i in range(256)}
    last_code = 256
    decoded_bitstring = ''.join(f'{byte:08b}' for byte in encoded_bytes)

    result = ''
    carry = ''

    char_length = math.ceil(math.log2(max_codebook_length))

    chunks = [int(decoded_bitstring[i:i+char_length], 2) for i in range(0, len(decoded_bitstring), char_length)]
    old = chunks.pop(0)
    result += code[old]

    for chunk in chunks:
        if chunk in code:
            word = code[chunk]
        else:
            word = code[old] + carry

        result += word
        carry = word[0]

        if last_code >= max_codebook_length:
            old = chunk
            continue

        code[last_code] = code[old] + carry
        last_code += 1
        old = chunk

    print(code)

    return ''.join(result)


def decode_new(encoded_bytes, max_codebook_length = 2 ** 12):
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
        new = int(decoded_bitstring[i:i + char_length], 2)

        if new in reverse_codebook:
            word_literal = reverse_codebook[new]
        else:
            if carry is not None:
                word_literal = codebook[old] + [carry]
            else:
                word_literal = codebook[old]

        result.append(word_literal)
        carry = word_literal[0]

        if last_code >= max_codebook_length:
            old = (new,)
            continue

        codebook[(*old, carry)] = last_code
        reverse_codebook[last_code] = (*old, carry)
        last_code += 1
        old = (new,)

    return ''.join(chr(char) for char in flatten(result))

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
            new = int(decoded_bitstring[i:i+char_length].ljust(char_length, '0'), 2)
        else:
            new = int(decoded_bitstring[i:i+char_length], 2)

        if new in reverse_codebook:
            word_literal = reverse_codebook[new]
        else:
            if carry is not None:
                word_literal = codebook[old] + [carry]
            else:
                word_literal = codebook[old]

        word_literal = tuples_to_string(word_literal, reverse_codebook)
        for char in word_literal:
            result.append(char)
        carry = word_literal[0]

        if last_code >= max_codebook_length:
            old = (new,)
            continue

        codebook[(*old, carry)] = last_code
        reverse_codebook[last_code] = (*old, carry)
        last_code += 1
        old = (new,)

    return ''.join(chr(char) for char in flatten(result))


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
    with open('plik', 'rb') as file:
        text = file.read()
    # text = 'zazolc gesla jazn, kocham jesc placki. placek to ja jestem.'

    max_codebook_length = 2 ** 12

    encoded_text, codebook = encode(text, max_codebook_length)

    with open('plik.bin', 'wb') as file:
        file.write(encoded_text)

    with open('plik.bin', 'rb') as file:
        text = file.read()

    decoded_text = decode_letters(text, max_codebook_length)
    with open('plik.out', 'w') as file:
        file.write(decoded_text)
    print(decoded_text[:1000])
