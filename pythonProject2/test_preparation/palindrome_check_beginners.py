# import sys
# sys.stdin = open("palindrome_check_beginners_input.txt")

def palindrome(word):
    N = len(word)
    for i in range(N):
        flag = True
        if word[i] != word[N-1-i]:
            flag = False
            break
        if flag:
            return 1
    return 0

T = int(input())
for tc in range(1, T+1):
    word = list(input())

    print(f'#{tc} {palindrome(word)}')