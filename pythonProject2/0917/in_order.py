import sys;sys.stdin = open("in_order_input.txt")

# 강사님 풀이
def inorder(v):
    if v <= N:
        global ans
        inorder(2 * v)
        ans += tree[v]
        inorder(2 * v + 1)

T = 10
for tc in range(1, T+1):
    N = int(input())
    tree = [''] * (N+1)
    for i in range(N):
        tmp = list(input().split())
        tree[int(tmp[0])] = tmp[1]

# 강사님 풀이
    ans = ''
    inorder(1)
    print(f'#{tc} {ans}')