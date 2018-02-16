from math import sqrt
from itertools import count, islice


def is_prime(n):
    # TODO: Use indy-crypto to check for prime
    # Taken from https://stackoverflow.com/a/27946768
    return n > 1 and all(n % i for i in islice(count(2), int(sqrt(n) - 1)))


def update_accumulator_val(accumulated, new_val, modulus):
    return (accumulated**new_val) % modulus
