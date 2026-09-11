import sys
sys.stdin = open("GNS_input.txt")

digits = ["ZRO", "ONE", "TWO", "THR", "FOR", "FIV", "SIX", "SVN", "EGT", "NIN"]

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    txt = list(map(str, input().split()))

    num_dict = {}
    for num in digits:
        num_dict[num] = 0

    for t in txt:
        if t in num_dict:
            num_dict[t] += 1

    ans = []
    for num in digits:
        if num_dict[num] != 0:
            while num_dict[num] != 0:
                ans.append(num)
                num_dict[num] -= 1

    # print(num_dict)
    print(f'#{tc}')
    print(*ans)

# # 강사님 풀이
#     # 카운팅
#     cnts = [0] * 10
#     for i in range(N):
#         for j in range(10):
#             if txt[i] == digits[j]:
#                 cnts[j] += 1
#     # 출력
#     print(f'#{tc}')
#     for i in range(10):
#         for j in range(cnts[i]):
#             print(digits[i], end=' ')
#     print()