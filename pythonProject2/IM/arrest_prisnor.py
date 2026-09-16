import sys
sys.stdin = open("arrest_prisnor_input.txt")

di = [0, 1, 0, -1]
dj = [1, 0, -1, 0]

pipe = [[], [0,1,2,3], [1,3], [0,2], [0,3], [0,1], [1,2], [2,3],]

def f(N, M, R, C, L):
    q = [(R, C)]    # 맨홀 뚜껑
    v = [[0] * M for _ in range(N)]     # 시간대별 진행가능 위치 표시
    v[R][C] = 1
    cnt = 0         # 위치할 수 있는 총 영역 수
    while q:        # 확인할 위치가 남아있으면
        i, j = q.pop(0)
        cnt += 1
        if v[i][j] < L:     # 아직 시간이 남아있으면
            for x in pipe[tunnel[i][j]]:    # 파이프 모양에 따라 새롭게 진입할 칸 확인
                ni = i + di[x]
                nj = j + dj[x]
                if 0 <= ni < N and 0 <= nj < M and tunnel[ni][nj] == 0 and v[ni][nj] == 0 and (x + 2) % 4 in pipe[tunnel[ni][nj]]:
                    q.append((ni,nj))
                    v[ni][nj] = v[i][j] + 1     # 이동할 수 있는 칸에 시간
    return cnt

T = int(input())
for tc in range(1, T+1):
    N, M, R, C, L = map(int, input().split())
    tunnel = [list(map(int, input().split())) for _ in range(N)]

    r = f(N, M, R, C, L)
    print(f'#{tc} {r}')