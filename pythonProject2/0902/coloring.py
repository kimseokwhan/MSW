import sys
sys.stdin = open("coloring_input.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    # 10 x 10 을 0으로 초기화
    arr = [([0] * 10) for _ in range(10)]
    # 왼쪽위좌표, 오른쪽아래좌표, 색상 받아서 칠하기
    for _ in range(N):
        r1, c1, r2, c2, color = map(int, input().split())
        # 색칠하기 : 2중 for문으로 색칠하기
        for i in range(r1, r2+1):
            for j in range(c1, c2+1):
                arr[i][j] += color

    # 겹쳐진 색상(3) 갯수 구하기
    cnt = 0
    for i in range(10):
        for j in range(10):
            if arr[i][j] == 3:
                cnt +=1

    print(f'#{tc} {cnt}')


# # 강사님 풀이
#     # 색칠하기
#     # 왼쪽위좌표, 오른쪽아래좌표, 색상 받아서 칠하기
#     for _ in range(N):
#         r1, c1, r2, c2, color = map(int, input().split())
#         # 색칠하기 : 2중 for문으로 색칠하기
#         for i in range(r1, r2+1):   # 행
#             for j in range(c1, c2+1):   # 열
#                 arr[i][j] += color  # 기존값에서 누적 -> 겹쳐진 부분이 보임
#
#     # 카운팅
#     cnt = 0
#     for i in range(10):
#         for j in range(10):
#             if[i][j] == 3:
#                 cnt += 1
#     print(cnt)