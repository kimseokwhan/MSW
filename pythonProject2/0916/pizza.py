import sys
sys.stdin = open("pizza_input.txt")

T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())
    Ci = list(map(int, input().split()))

    oven = []
    last = 0

    for i in range(N):
        oven.append(i)
        last += 1

    while len(oven) != 1:
        idx = oven.pop(0)
        Ci[idx] = Ci[idx] // 2
        if Ci[idx] > 0:
            oven.append(idx)
        else:
            if last < M:
                oven.append(last)
                last += 1

    print(f'#{tc} {oven.pop() + 1}')