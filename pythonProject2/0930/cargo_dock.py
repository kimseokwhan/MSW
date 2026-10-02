import sys; sys.stdin = open("cargo_dock_input.txt")

# T = int(input())
# for tc in range(1, T+1):
#     N = int(input())
#     se = [list(map(int, input().split())) for _ in range(N)]
#
#     se.sort(key=lambda x:x[1], reverse=False)
#
#     ans = 0
#     curtime = 0
#     for i in range(N):
#         if curtime <= se[i][0]:
#             curtime = se[i][1]
#             ans += 1
#
#     print(f'#{tc} {ans}')


# 강사님 풀이
# arr.sort(key=lambda x:(x[1], x[0]))   # 두개 기준으로 정렬할 때 (앞에 있는걸 1번 기준, 뒤에 있는걸 2번 기준)
T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    arr.sort(key=lambda x:x[1])     # 종료시간순으로 정렬

    ans = last = 0
    for i in range(N):
        if last <= arr[i][0]:
            ans += 1
            last = arr[i][1]
    print(f'#{tc} {ans}')