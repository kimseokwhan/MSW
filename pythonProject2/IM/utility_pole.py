import sys
sys.stdin = open("utility_pole_input.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())    # 전선의 개수, 1 ≤ N ≤1000
    AB = [list(map(int, input().split())) for _ in range(N)]

    # A 전봇대에 연결된 전선 높이 기준 오름차순 정렬
    AB.sort()
    cnt = 0
    for i in range(1, N):   # A 전봇대 기준 오름파순 정렬된 순서로
        for j in range(i):  # A에서는 낮지만 B에서는 더 높은 경우, j는 A에서 더 낮은 전선들
            if AB[j][1] > AB[i][1]:
                cnt += 1
    print(f'#{tc} {cnt}')