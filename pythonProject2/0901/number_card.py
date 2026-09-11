import sys
sys.stdin = open("number_card_input.txt", "r")

T = int(input())
# 여러개의 테스트 케이스가 주어지므로, 각각을 처리합니다.
for test_case in range(1, T + 1):
    N = int(input())
    # arr = list(map(int, input()))   # 붙어있으면 split 빼기
    num_str = str(input())
    arr = []
    for n in num_str:
        arr.append(int(n))

    # print(N)
    # print(num_str)
    # print(arr)

    counts = [0] * 10
    for i in range(N):
        counts[arr[i]] += 1

    # print(counts)

    # max = counts[0]
    # max_index = 0
    #
    # for j in range(10):
    #     if max <= counts[j]:
    #         max = counts[j]
    #         max_index = j
    #
    # # print(max)
    # # print(max_index)
    #
    # print(f"#{test_case} {max_index} {max}")

# 강사님 풀이
    max_i = 0
    for i in range(1, 10):
        if counts[max_i] <= counts[i]:
            max_i = i

    print(f"#{test_case} {max_i} {counts[max_i]}")