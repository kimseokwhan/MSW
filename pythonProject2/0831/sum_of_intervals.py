import sys
sys.stdin = open("sum_of_intervals_input.txt", "r")   # "r" 생략 가능 (r = read)
# sys.stdout = open("sum_of_intervals_output.txt", "w") # 출력 파일로 (w = write)

T = int(input())
# 여러개의 테스트 케이스가 주어지므로, 각각을 처리합니다.
for test_case in range(1, T + 1):
    N, M = map(int, input().split())
    arr = list(map(int, input().split()))

    # print(N, M)
    # print(arr)

    sum_list = []
    for i in range(N-(M-1)):
        sum_inter = 0
        for j in range(i, i+M):
            sum_inter += arr[j]

        sum_list.append(sum_inter)

        # print(sum_inter)
    # print(sum_list)

    max_sum = sum_list[0]
    min_sum = sum_list[0]
    for m in sum_list:
        if m > max_sum:
            max_sum = m
        if m < min_sum:
            min_sum = m

    total = max_sum - min_sum

    print(f"#{test_case} {total}")


# # 강사님 풀이
#     max_v = float('-inf')
#     min_v = float('inf')
#     for i in range(N-M+1):
#         sum_v = 0   # 구간 합계의 초기화
#         for j in (M):
#             sum_v += arr[i+j]
#         if max_v < sum_v:
#             max_v = sum_v
#         if min_v > sum_v:
#             min_v = sum_v
#     print(f"#{test_case} {max_v - min_v}")