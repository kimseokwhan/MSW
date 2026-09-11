import sys
sys.stdin = open("string_comparison_input.txt")

def s_find(p, t):
    N = len(t)
    M = len(p)

    for i in range(N-M+1):
        flag = True
        for j in range(M):
            if p[j] != t[i+j]:
                flag = False
                break
        if flag:
            return 1
    return 0

T = int(input())
for tc in range(1, T+1):
    p = input()     # pattern
    t = input()     # text

    # cnt = 0

    # if s1 in s2:
    #     cnt += 1

    # print(f'#{tc} {cnt}')

    print(f'#{tc} {s_find(p, t)}')

    # print(f'#{tc} {my_find(p, t)}')

# # 강사님 풀이
# def my_find(p, t):  # 텍스트.find(패턴)
#     N = len(t)
#     M = len(p)
#     # 텍스트를 순회
#     for i in range(N-M+1):
#         flag = True     # 패턴 순회
#         for j in range(M):
#             if p[j] != t[i+j]:
#                 flag = False
#                 return i
#                 break
#         if flag:    # 찾았을 때
#             return i
#         # break(o), break(x)
#     return -1   # 못 찾았을 때
