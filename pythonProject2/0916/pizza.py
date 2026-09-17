import sys
sys.stdin = open("pizza_input.txt")

# 강사님 풀이
def pizza(Ci, M):
    Q = []
    for i in range(N):
        Q.append((i, Ci[i]))
    last = N     # 다음 화덕에 넣을 치즈 번호
    while len(Q) != 1:
        idx, cheese = Q.pop(0)      # 피자 꺼내기
        Ci[idx] = cheese // 2
        # 치즈가 남으면 다시 넣기
        if Ci[idx] != 0:
            Q.append((idx, Ci[idx]))
        # 치즈가 다 녹았으면 다음 피자 넣기
        elif last < M:
            Q.append((last, Ci[last]))
            last += 1
    return Q.pop()

T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())
    Ci = list(map(int, input().split()))

    # oven = []
    # last = 0
    #
    # for i in range(N):
    #     oven.append(i)
    #     last += 1
    #
    # while len(oven) != 1:
    #     idx = oven.pop(0)
    #     Ci[idx] = Ci[idx] // 2
    #     if Ci[idx] > 0:
    #         oven.append(idx)
    #     else:
    #         if last < M:
    #             oven.append(last)
    #             last += 1
    #
    # print(f'#{tc} {oven.pop() + 1}')


# 강사님 풀이
    ans, _ = pizza(Ci, M)
    print(f'#{tc} {ans + 1}')