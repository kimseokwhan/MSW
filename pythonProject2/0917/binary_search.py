import sys
sys.stdin = open("binary_search_input.txt")

def f(T, a):
    if T > N:
        return 0
    l = f(T * 2, a)
    tree[T] = l + a + 1
    r = f(T * 2 + 1, tree[T])
    return l + r + 1

T = int(input())
for tc in range(1, T+1):
    N = int(input())

    tree = [0] * (N + 1)

    f(1, 0)
    print(f'#{tc} {tree[1]} {tree[N//2]}')