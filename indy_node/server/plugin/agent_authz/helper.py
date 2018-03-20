from math import sqrt
from itertools import count, islice
from indy_crypto.big_number import BigNumber


def is_prime(n):
    # TODO: Use indy-crypto to check for prime
    # Taken from https://stackoverflow.com/a/27946768
    # return n > 1 and all(n % i for i in islice(count(2), int(sqrt(n) - 1)))
    return BigNumber.is_prime(n)


def update_accumulator_val(accumulated, new_val, modulus):
    # TODO: Use indy-crypto for this calculation
    # return (accumulated**new_val) % modulus
    return BigNumber.modular_exponentiation(accumulated, new_val, modulus)
