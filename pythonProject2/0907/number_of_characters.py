import sys
sys.stdin = open("number_of_characters_input.txt")

T = int(input())
for tc in range(1, T+1):
    s1 = input()
    s2 = input()
    N = len(s1)
    M = len(s2)

    ans = 0
    for i in range(N):
        cnt = 0
        for j in range(M):
            if s1[i] == s2[j]:
                cnt += 1
        if ans < cnt:
            ans = cnt

    print(f'#{tc} {ans}')