import sys; sys.stdin = open("도너츠_in.txt")

T = int(input())
for tc in range(1, T+1):
    N, M, K = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(N)]

    ans = 0
    for i in range(N-K+1):      # 농작물
        for j in range(M-K+1):
            Sum = 0
            for a in range(i, i+K):     # 도너츠 모양
                for b in range(j, j+K):
                    if a == i or a == (i+K-1) or b == j or b == (j+K-1):
                        Sum += arr[a][b]
            ans = max(ans, Sum)

    print(f'#{tc} {ans}')