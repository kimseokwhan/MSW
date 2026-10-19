import sys; sys.stdin = open("adv2_in.txt")
# 배열을 돌면서, 연료 최소 낭비 구조
# 높이가 같으면 1 소비, 낮은 곳은 소비 X, 높은 곳은 차이 2배만큼 소비

dr = [0, 1, 0, -1]
dc = [1, 0, -1, 0]

T = int(input())

for tc in range(1, T + 1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    visited = [[0] * N for _ in range(N)]
    dist = [[float('inf')] * N for _ in range(N)]
    dist[0][0] = 0

    for _ in range(N * N):
        min_oil = float('inf')
        r = c = -1

        # 1. 방문하지 않은 칸 중 최소 연료 위치 찾기
        for i in range(N):
            for j in range(N):
                if not visited[i][j] and dist[i][j] < min_oil:
                    min_oil = dist[i][j]
                    r, c = i, j

        if r == -1:
            break
        if r == N - 1 and c == N - 1:
            break
        visited[r][c] = 1

        # 2. 상하좌우 탐색
        for d in range(4):
            nr = r + dr[d]
            nc = c + dc[d]
            if 0 <= nr < N and 0 <= nc < N:
                if visited[nr][nc]:
                    continue
                # 3. 이동 연료 계산
                diff = arr[nr][nc] - arr[r][c]
                if diff > 0:
                    cost = diff * 2
                elif diff == 0:
                    cost = 1
                else:
                    cost = 0
                # 4. 더 적은 연료라면 갱신
                new_oil = dist[r][c] + cost
                if new_oil < dist[nr][nc]:
                    dist[nr][nc] = new_oil

    print(f'#{tc} {dist[N - 1][N - 1]}')

# def rescu(r, c, oil):
#     global min_oil
#     # 1. 현재 연료가 이미 최소 연료 이상이면 중단
#     if oil >= min_oil:
#         return
#     # 2. 목적지에 도착하면 최소 연료 갱신
#     if r == N - 1 and c == N - 1:
#         min_oil = oil
#         return
#     visited[r][c] = 1
#     # 3. 상하좌우 탐색
#     for d in range(4):
#         nr = r + dr[d]
#         nc = c + dc[d]
#         if 0 <= nr < N and 0 <= nc < N:
#             if visited[nr][nc] == 0:
#                 # 이동할 때 필요한 연료 계산
#                 diff = arr[nr][nc] - arr[r][c]
#                 if diff > 0:
#                     cost = diff * 2
#                 elif diff == 0:
#                     cost = 1
#                 else:
#                     cost = 0
#                 # 현재 경로의 연료를 별도로 계산
#                 new_oil = oil + cost
#                 rescu(nr, nc, new_oil)
#     # 다른 경로에서도 이 칸을 사용할 수 있도록 복구
#     visited[r][c] = 0
#
# dr = [0, 1, 0, -1]
# dc = [1, 0, -1, 0]
#
# T = int(input())
# for tc in range(1, T + 1):
#     N = int(input())
#     arr = [list(map(int, input().split())) for _ in range(N)]
#
#     visited = [[0] * N for _ in range(N)]
#     min_oil = float('inf')
#     rescu(0, 0, 0)
#     print(f'#{tc} {min_oil}')


"""
산악 구조를 위한 로봇이 있다. 연료 소모를 적게 하면서 조난자에게 이동하려고 한다.
N x N 정방형의 지도 정보가 주어지는데, 땅의 높이를 값으로 갖는다.
로봇은 상, 하, 좌, 우로만 이동할 수 있다.
현재 위치에서 높이가 같은 곳으로 이동할 때에는 연료가 1 소모되고, 낮은 곳으로 이동할 때에는 연료가 소모되지 않는다.
그리고 높은 곳으로 이동할 때에는, 높이 차의 두 배만큼 연료가 소모된다.
로봇의 출발지는 (1, 1)로 고정되어 있고, 조난자의 위치도 (N, N)로 고정된다.
조난자의 위치까지 최소 연료를 소비하는 경로를 찾고, 소모된 연료 값을 출력하는 프로그램을 작성하라.
[제약 사항]
1.     지도의 가로, 세로 길이 N은 4이상 30이하의 정수이다. (4 ≤ N ≤ 30)
2.     땅의 높이는 0이상 9이하의 정수이다.
3.     로봇은 대각선 방향으로 이동할 수 없다.
4.      
[예제 1]
아래와 같이 N이 4인 지도 정보가 주어진 경우를 살펴 보자.
이 경우에 최소 연료로 이동하는 경로는 다음과 같다. 9 -> 8 -> 7 -> 6 -> 5 -> 4까지는 연료가 소모되지 않고,
4 -> 5를 이동할 때는 높은 곳으로 이동하기 때문에 높이 차이인 1의 두 배가 소모되어 2가 소모된다. 따라서 총 소모 연료는 2가 된다.
[예제 2]
아래와 같이 N이 6인 지도 정보가 주어진 경우를 살펴 보자.
이 경우에 최소 연료로 이동하는 경로는 다음과 같다. 모두 높이가 같기 때문에 연료가 1씩 소모된다. 따라서 총 소모 연료는 16이 된다.
[입력]
가장 첫 줄에는 테스트 케이스의 개수 T가 주어지고, 그 아래로 각 테스트 케이스가 주어진다.
각 테스트 케이스의 첫 번째 줄에는 지도의 한 변의 길이 N이 주어진다.
그 다음 N x N의 높이 값이 주어진다. (0 ~ 9 값을 갖는 N x N 2차원 지도 정보)
[출력]
출력의 각 줄은 '#t'로 시작하고, 공백을 한 칸 둔 다음 정답을 출력한다.
(t는 테스트 케이스의 번호를 의미하며 1부터 시작한다.)
[입출력 예]
입력 예
출력 예
5              // 테스트 케이스의 개수 T = 5
4              // 1번째 테스트 케이스, 지도 한 변의 길이 N=4
9 5 7 9
8 4 2 5
7 6 5 4
8 8 9 5
6              // 2번째 테스트 케이스, 지도 한 변의 길이 N=6
1 1 1 1 1 1
9 9 9 9 9 1
9 9 1 1 1 1
9 9 1 9 9 9
9 9 1 9 9 9
9 9 1 1 1 1
…             // 이하 sample_input.txt 참조
#1 2
#2 16
#3 32
#4 66
#5 93
"""