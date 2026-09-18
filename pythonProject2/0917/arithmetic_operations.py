import sys;sys.stdin = open("arithmetic_operations_input.txt")

# 강사님 풀이
def calc(op, left, right):
    if op == '+':
        return left + right
    elif op == '-':
        return left - right
    elif op == '*':
        return left * right
    elif op == '/':
        return left / right

def postorder(v):
    if left[v] == 0 and right[v] == 0:
        return operator[v]
    else:
        l = postorder(left[v])
        r = postorder(right[v])
        operator[v] = calc(operator[v], l, r)
        return operator[v]

T = 10
for tc in range(1, T+1):
    N = int(input())


# 강사님 풀이
    left = [0] * (N + 1)
    right = [0] * (N + 1)
    operator = [0] * (N + 1)

    for i in range(N):
        tmp = list(input().split())
        idx = int(tmp[0])
        if tmp[1] == '+' or tmp[1] == '-' or tmp[1] == '*' or tmp[1] == '/':
            operator[idx] = tmp[1]
            left[idx] = int(tmp[2])
            right[idx] = int(tmp[3])
        else:
            operator[idx] = int(tmp[1])

    ans = postorder(1)
    print(f'#{tc} {int(ans)}')