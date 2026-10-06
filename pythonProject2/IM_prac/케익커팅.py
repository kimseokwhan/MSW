import sys
sys.stdin = open("케익커팅_in.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    ans = 0
    for i in range(1, N):
        for j in range(1, N):
            sum1 = 0
            sum2 = 0
            sum3 = 0
            sum4 = 0
            for k in range(N):
                for l in range(N):
                    if i < k and j < l:
                        sum1 += arr[k][l]
                    if i < k and j >= l:
                        sum2 += arr[k][l]
                    if i >= k and j < l:
                        sum3 += arr[k][l]
                    if i >= k and j >= l:
                        sum4 += arr[k][l]
            if sum1 == sum2 == sum3 == sum4:
                ans = 1
                break

    print(f'#{tc} {ans}')