import math
import glob
from collections import Counter


def count_element_probability(elements):
    element_counts = Counter(elements)
    total_elements = sum(element_counts.values())

    for element in element_counts:
        element_counts[element] /= total_elements

    return {key: value for key, value in element_counts.items()}


def calculate_entropy(probabilities):
    entropy_values = [value * math.log(value, 2) for value in probabilities.values()]
    total_entropy = -sum(entropy_values)

    return total_entropy


def count_group_following_elements(content, group_size):
    groups = {}

    for i in range(0, len(content) - group_size):
        group = tuple(content[i:i + group_size])
        following_element = content[i + group_size]

        if group in groups:
            following_elements = groups[group]

            if following_element in following_elements:
                following_elements[following_element] += 1
            else:
                following_elements[following_element] = 1
        else:
            groups[group] = {following_element: 1}

    return groups


def calculate_probabilities(groups, counter):
    probabilities = {}
    group_probabilities = {}

    for group, following_chars in groups.items():
        group_occurrences = sum(following_chars.values())

        for char, count in following_chars.items():
            following_chars[char] = count / group_occurrences

        group_probabilities[group] = group_occurrences / counter
        probabilities[group] = following_chars

    return probabilities, group_probabilities


def calculate_conditional_entropy(probabilities, groups):
    entropy_sum = 0.0

    for group, probability in groups.items():
        for value in probabilities[group].values():
            entropy_sum += probability * value * math.log(value, 2)

    return -entropy_sum


if __name__ == '__main__':
    with open('data/norm_wiki_en.txt', 'r') as file:
        text = file.read()

    letters_probabilities = count_element_probability(text)
    letter_entropy = calculate_entropy(letters_probabilities)

    print('Letter entropy:', letter_entropy)

    words = text.split()
    words_probabilities = count_element_probability(words)
    word_entropy = calculate_entropy(words_probabilities)

    print('Word entropy:', word_entropy)

    files = glob.glob('data/*.txt')
    group_sizes = range(1, 5)

    for file_name in files:
        print('\n', file_name)
        with open(file_name, 'r') as file:
            chars = file.read()
        words = chars.split()

        for group_size in group_sizes:
            elements = count_group_following_elements(chars, group_size)
            group_count = len(chars) - group_size + 1

            probabilities, keys = calculate_probabilities(elements, group_count)
            print(f'Conditional entropy of chars of {group_size} group size:', calculate_conditional_entropy(probabilities, keys))

            elements = count_group_following_elements(words, group_size)
            group_count = len(words) - group_size + 1

            probabilities, keys = calculate_probabilities(elements, group_count)
            print(f'Conditional entropy of words of {group_size} group size:', calculate_conditional_entropy(probabilities, keys))
