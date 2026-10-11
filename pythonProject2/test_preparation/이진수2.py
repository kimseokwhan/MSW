import sys; sys.stdin = open("이진수2_in.txt")

T = int(input())
for tc in range(1, T+1):
    num = float(input())

    result = ''
    while num > 0:
        if len(result) > 12:
            result = 'overflow'
            break

        num *= 2
        if num >= 1:
            result += '1'
            num -= 1
        elif num < 1:
            result += '0'

    print(f'#{tc} {result}')