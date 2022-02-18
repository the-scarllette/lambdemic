
def decimal_to_binary(value):
    result = ""
    while True:
        result = str(value % 2) + result
        value = value // 2
        if value < 1:
            return result
