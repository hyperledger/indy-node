from indy_crypto.big_number import BigNumber


def is_prime(n):
    return BigNumber.is_prime(n)


def update_accumulator_val(accumulated, new_val, modulus):
    return BigNumber.modular_exponentiation(accumulated, new_val, modulus)
