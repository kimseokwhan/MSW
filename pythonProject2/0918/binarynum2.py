import sys; sys.stdin = open("binarynum2_input.txt")

mapping = {
    '0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100',
    '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001',
    'A': '1010', 'B': '1011', 'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
}

T = int(input())
for tc in range(1, T+1):
    arr = float(input())

    result = ''

    while arr != 0:
        if len(result) == 13:
            result = 'overflow'
            break
        arr *= 2
        if arr >= 1:
            result += '1'
            arr -= 1
        else:
            result += '0'
            continue

    print(f'#{tc} {result}')