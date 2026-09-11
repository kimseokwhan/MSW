import sys
sys.stdin = open("flatten_input.txt", "r")

T = 10
for tc in range(1, T+1):
    N = int(input())
    arr = list(map(int, input().split()))

    for i in range(N):
        max_idx = 0
        min_idx = 0
        for j in range(len(arr)):
            if arr[max_idx] < arr[j]:
                max_idx = j
            if arr[min_idx] > arr[j]:
                min_idx = j
        arr[max_idx] -= 1
        arr[min_idx] += 1

    max_ans = arr[0]
    min_ans = arr[0]
    for k in range(len(arr)):
        if max_ans < arr[k]:
            max_ans = arr[k]
        if min_ans > arr[k]:
            min_ans = arr[k]
    ans = max_ans - min_ans
    print(f'#{tc} {ans}')


# # 강사님 풀이
# def min_max():
#     max_i = min_i = 0
#     for i in range(1, N):
#         if arr[max_i] < arr[i]:
#             max_i = i
#         if arr[min_i] > arr[i]:
#             min_i = i
#
#     return max_i, min_i
#
#
# T = 10
# # 여러개의 테스트 케이스가 주어지므로, 각각을 처리합니다.
# for tc in range(1, T + 1):
#     dump = int(input())    # 평탄화 횟수
#     N = 100
#     arr = list(map(int, input().split()))
#
#     # dump 수 만큼 평탄화 작업
#     for i in range(N):
#         max_i, min_i = min_max()
#         arr[max_i] -= 1
#         arr[min_i] += 1
#
#     # 평탄화가 끝난 후, 최대값과 최소값의 차이를 출력
#     max_i, min_i = min_max()
#     print(f"#{tc} {arr[max_i] - arr[min_i]}")