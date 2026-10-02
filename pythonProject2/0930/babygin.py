import sys; sys.stdin = open("babygin_input.txt")




















































# # 강사님 풀이
# def baby_test(cnts):
#     for i in range(10):     # triplet
#         if cnts[i] >= 3:
#             return True
#     for i in range(8):      # run, 7 8 9
#         if cnts[i] >= 1 and cnts[i + 1] >= 1 and cnts[i + 2] >= 1:
#             return True
#     return None
#
# def game(arr):
#     # 각 플레이어의 카운팅 변수
#     cnt1 = [0] * 10
#     cnt2 = [0] * 10
#     for i in range(len(arr)):   # 12
#         if i % 2 == 0:  # 플레이어1
#             cnt1[arr[i]] += 1
#         else:
#             cnt2[arr[i]] += 1
#         # 3장 이후부터 검사
#         if i >= 4:
#             if i % 2 == 0:
#                 if baby_test(cnt1):
#                     return 1
#             else:
#                 if baby_test(cnt2):
#                     return 2
#     return 0
#
# T = int(input())
# for tc in range(1, T+1):
#     arr = list(map(int, input().split()))
#
#     print(f'#{tc} {game(arr)}')