
def binary_to_decimal(value):
    return new_base_to_decimal(value, 2)


def decimal_to_binary(value):
    return decimal_to_new_base(value, 2)


def decimal_to_new_base(value, base):
    result = ""
    while True:
        result = str(value % base) + result
        value = value // base
        if value < 1:
            return result


def elongate_str(s, filler, length):
    while len(s) < length:
        s = filler + s
    return s


def new_base_to_decimal(value, base):
    value = str(int(value)).reverse()
    result = 0
    for i in range(len(value)):
        result += int(value[i])*(base**i)
    return result
