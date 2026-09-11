import sys
sys.stdin = open("sum_input.txt")

T = 10
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(100)]










































# 강사님 풀이
    ans = 0
    for i in range(100):
        sum_v = 0
        for j in range(100):
            sum_v += arr[i][j]
        if ans < sum_v:
            ans = sum_v

    sum_v = 0
    for i in range(100):
        sum_v += arr[i][i]
    if ans < sum_v:
        ans = sum_v

    sum_v = 0
    for i in range(100):
        sum_v += arr[100][100-1-i]
    if ans < sum_v:
        ans = sum_v