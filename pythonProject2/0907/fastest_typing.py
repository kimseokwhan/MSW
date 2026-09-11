import sys
sys.stdin = open("fastest_typing_input.txt")

# 강사님 풀이
def my_find(txt, pat, N, M):
    cnt = 0
    i = 0
    while i < (N-M+1):
        flag = True
        for j in range(M):
            if txt[i+j] != pat[j]:
                flag = False
                break
        if flag:
            cnt += 1
            i = i + M - 1
        i += 1
    return cnt

T = int(input())
for tc in range(1, T+1):
    txt, pat = map(str, input().split())
    N, M = len(txt), len(pat)

    cnt = my_find(txt, pat, N, M)
    ans = N - M * cnt + cnt

    print(f'#{tc} {ans}')