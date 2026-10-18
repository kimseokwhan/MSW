import sys; sys.stdin = open("농작물수확하기_in.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input())) for _ in range(N)]

    center = N // 2     # 중앙
    ans = 0
    for i in range(N):
        diff = abs(center - abs(i - center))    # 중앙에서 범위
        start = center - diff       # 행마다 시작 끝
        end = center + diff
        for j in range(start, end+1):
            ans += arr[i][j]

    print(f'#{tc} {ans}')