# # 강사님 힌트
# hex = '1'
# print(int(hex, 16))
# print(bin(int(hex, 16)))
#
# mapping = {
#     '0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100',
#     '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001',
#     'A': '1010', 'B': '1011', 'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
# }
#
# a = '1F'
# result = ''
# for i in range(len(a)):
#     result += mapping[a[i]]
# print(result)

import sys; sys.stdin = open("binarynum1_input.txt")

mapping = {
    '0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100',
    '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001',
    'A': '1010', 'B': '1011', 'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'
}

T = int(input())
for tc in range(1, T+1):
    N, arr = input().split()

    result = ''
    for i in range(len(arr)):
        result += mapping[arr[i]]

    print(f'#{tc} {result}')