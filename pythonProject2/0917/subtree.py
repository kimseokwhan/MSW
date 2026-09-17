import sys;sys.stdin = open("subtree_input.txt")

# def f(T):
#     if T == 0:
#         return 0
#     l = f(c1[T])
#     r = f(c2[T])
#     return l + r + 1

def pre_order(T):
    global cnt
    if T:
        cnt += 1
        pre_order(c1[T])
        pre_order(c2[T])

T = int(input())
for tc in range(1, T+1):
    E, N = map(int, input().split())
    arr = list(map(int, input().split()))

    c1 = [0] * (E+2)
    c2 = [0] * (E+2)

    for i in range(E):
        p, c = arr[i * 2], arr[i * 2 + 1]
        if c1[p] == 0:
            c1[p] = c
        else:
            c2[p] = c

    # ans = f(N)

    cnt = 0
    pre_order(N)

    print(f'#{tc} {cnt}')