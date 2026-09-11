import sys
sys.stdin = open("paper_pasting_input.txt")

# # 강사님 풀이 (수학적 귀납법)
# def f(n):
#     if n <= 1:  # f(0) =1, f(1) = 1
#         return 1
#     else:
#         return f(n-1) + 2*f(n-2)

# 강사님 풀이 (DP)
m = [1, 1]
for i in range(2, 31):
    m.append(m[i-1] + 2*m[i-2])

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    # print(f'#{tc} {f(N // 10)}')
    print(f'#{tc} {m[N // 10]}')