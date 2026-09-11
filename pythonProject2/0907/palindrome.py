import sys
sys.stdin = open("palindrome_input.txt")

def palin(text):
    N = len(text)
    for i in range(N):
        flag = True
        if text[i] != text[N-1-i]:
            flag = False
            break
        if flag:
            return 1
    return 0

T = int(input())
for tc in range(1, T+1):
    # text = list(map(str, input()))
    text = list(input())

    # print(text)
    print(f'#{tc} {palin(text)}')

    # print(f'#{tc} {palindrome(text)}')

# # 강사님 풀이
# def palindrome(text):
#     N = len(text)
#     flag = True
#     for i in range(N//2):
#         if text[i] != text[N-1-i]:
#             flag = False
#             break
#         if flag: return 1
#     return 0
