import sys
sys.stdin = open("palindrome1_input.txt")

# 강사님 풀이
def row_count(arr):
    cnt = 0
    for i in range(N):
        for j in range(N-M+1):
            flag = True
            for k in range(M//2):
                if arr[i][j+k] != arr[i][j+M-1-k]:
                    flag = False
                    break
            if flag:
                cnt += 1
    return cnt

def col_count(arr):
    cnt = 0
    for i in range(N):
        for j in range(N-M+1):
            flag = True
            for k in range(M//2):
                if arr[j+k][i] != arr[j+M-1-k][i]:
                    flag = False
                    break
            if flag:
                cnt += 1
    return cnt

T = 10
for tc in range(1, T+1):
    N = 8
    M = int(input())
    arr = [list(input()) for _ in range(N)]

    ans = 0
    ans += row_count(arr)
    ans += col_count(arr)

    print(f'#{tc} {ans}')