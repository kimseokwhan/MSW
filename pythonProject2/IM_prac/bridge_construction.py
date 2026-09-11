import sys
sys.stdin = open("bridge_construction_input.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    for k in range(1, 6):
        print(f'#{k} {arr.count(k)}')

    for i in range(N):
        for j in range(N):
            for k in range(1, 6):
                pass