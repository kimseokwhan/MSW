import sys
sys.stdin = open("clearing_repeated_input.txt")

T = int(input())
for tc in range(1, T+1):
    txt = input()

    # print(txt)

    top = -1
    stack = [0] * 1000

    for x in txt:
        top += 1
        stack[top] = x
        if stack[top] == stack[top - 1]:
            top -= 2

    cnt = top + 1   # top은 위치이기 때문에 + 1

    print(f'#{tc} {cnt}')


# # 강사님 풀이
#     stack = []
#     for tok in txt:
#         # push
#         if not stack or tok != stack[-1]:
#             stack.append(tok)
#         else:   # pop
#             stack.pop()
#     print(f'#{tc} {len(stack)}')