import sys
sys.stdin = open("minimum_sum_input.txt")

# def dfs(r, c, cursum):
#     global least    # 최소값 글로벌 선언 (그래야 초기화 안됨)
#     if least < cursum:  # 가지치기 (현재 더해지고 있는 값이 최소값을 넘으면 그냥 끝)
#         return
#     if r == N-1 and c == N-1:   # r, c가 맨 마지막에 도착하면 끝
#         if least > cursum:      # 맨 마지막에 도착했을 때 값이 원래의 최소값보다 작으면
#             least = cursum      # 최소값에 대입
#         return
#     if r+1 < N:     # r가 벽에 안닿았으면 r에 +1     (r이 벽에 닿아도 c는 증가해야 하니까 r,c 조건 따로 선언)
#         dfs(r+1, c, cursum + arr[r+1][c])
#     if c+1 < N:     # c가 벽에 안닿았으면 c에 +1
#         dfs(r, c+1, cursum + arr[r][c+1])
#
#
# T = int(input())
# for tc in range(1, T+1):
#     N = int(input())
#     arr = [list(map(int, input().split())) for _ in range(N)]
#
#     least = float('inf')    # 최소값 구할 변수 (인피니티값 넣어 놓음)
#     dfs(0, 0, arr[0][0])    # dfs 함수 (r, c, cursum(0,0 값 넣어서 시작)
#     print(f'#{tc} {least}')


# 강사님 풀이
def dfs(r, c, cursum):
    global ans
    if ans < cursum:
        return
    if r == N-1 and c == N-1:
        ans = min(ans, cursum)
        return
    if c+1 < N:
        dfs(r, c+1, cursum + arr[r][c+1])
    if r+1 < N:
        dfs(r+1, c, cursum + arr[r+1][c])

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    ans = float('inf')
    dfs(0, 0, arr[0][0])
    print(ans)
