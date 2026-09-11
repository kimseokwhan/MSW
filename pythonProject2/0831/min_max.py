import sys
sys.stdin = open("min_max_input.txt", "r")

T = int(input())
# 여러개의 테스트 케이스가 주어지므로, 각각을 처리합니다.
for test_case in range(1, T + 1):
    N  = int(input())
    arr = list(map(int, input().split()))

    # print(N)
    # print(arr)

    max = arr[0]
    min = arr[0]

    for i in arr:
        if i > max:
            max = i

        if i < min:
            min = i

    print(f"#{test_case} {max - min}")