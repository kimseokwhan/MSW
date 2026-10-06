import sys
sys.stdin = open("electric_bus2_input.txt")

# def charge(cur, battery, cnt):
#     global min_cnt, N
#     if min_cnt < cnt:
#         return
#     if battery == 0:
#         return
#     elif cur == N-1 and battery >= 1:
#         if min_cnt > cnt:
#             min_cnt = cnt
#         return
#
#     charge(cur + 1, battery - 1, cnt)
#     charge(cur + 1, Ni[cur + 1], cnt + 1)
#
#
# T = int(input())
# for tc in range(1, T + 1):
#     Ni = list(map(int, input().split()))
#
#     N = Ni[0]
#     min_cnt = float('inf')
#
#     charge(1, Ni[1], 0)  # 현재 위치, 배터리 잔량
#
#     print(f'#{tc} {min_cnt}')


# 강사님 풀이
def dfs(lev, e, cnt):
    global ans
    if ans <= cnt: return    # 가지치기
    if lev == N:
        ans = min(ans, cnt)
        return
    # 충전하기
    dfs(lev+1, arr[lev]-1, cnt+1)
    # 충전하지 않고 통과 (배터리가 남아 있어야)
    if e > 0:
        dfs(lev + 1, e-1, cnt)

T = int(input())
for tc in range(1, T+1):
    arr = list(map(int, input().split()))
    N = arr[0]
    ans = float('inf')
    dfs(2, arr[1]-1, 0)

    print(f'#{tc} {ans}')