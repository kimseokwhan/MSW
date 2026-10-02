import sys
sys.stdin = open("binary_search_input.txt")

def binary_search(a, key):
    l, r = 0, len(a) - 1
    dir = -1  # 방향미정, 왼쪽: 0, 오른쪽: 1
    while l <= r:
        m = (l + r) // 2
        if key == a[m]:
            return 1
        elif key < a[m]:  # 왼쪽: 같은 방향일 때 멈춤
            if dir == 0:
                return 0
            else:
                r = m - 1
                dir = 0
        elif key > a[m]:  # 오른쪽
            if dir == 1:
                return 0
            else:
                l = m + 1
                dir = 1
    return 0


T = int(input())
for tc in range(1, T + 1):
    N, M = map(int, input().split())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    A.sort()
    cnt = 0
    for i in range(M):
        cnt += binary_search(A, B[i])
    print(f'#{tc} {cnt}')
