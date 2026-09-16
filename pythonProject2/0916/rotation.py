import sys
sys.stdin = open("rotation_input.txt")

T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())
    que = list(map(int, input().split()))

    # ans = que[M % N]
    # print(f'#{tc} {ans}')
    #
    # print(f'#{tc} {que[M % N]}')

    # for i in range(M):
    #     que.append(que.pop(0))
    # print(f'#{tc} {que[0]}')