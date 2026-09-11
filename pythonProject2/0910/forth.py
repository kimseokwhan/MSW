import sys
sys.stdin = open("forth_input.txt")

icp = {'(':3, '*':2, '/':2, '+':1, '-':1}   # in-comming priority
isp = {'(':0, '*':2, '/':2, '+':1, '-':1}   # in-stack priority     # 중위를 후위로 바꿀때 필요


# # 강사님 풀이
# def forth(code):
#     stack = []
#     for tok in code:
#         # 1. 숫자 -> push
#         if tok.isdigit():
#             stack.append(tok)
#         # 2. 연산자 -> 2개 pop -> 계산후 push
#         elif tok in '+-*/':
#             if len(stack) < 2:
#                 return 'error'
#             else:
#                 op2 = int(stack.pop())
#                 op1 = int(stack.pop())
#                 if tok == '+':
#                     stack.append(op1 + op2)
#                 elif tok == '-':
#                     stack.append(op1 - op2)
#                 elif tok == '*':
#                     stack.append(op1 * op2)
#                 elif tok == '/':
#                     stack.append(op1 // op2)
#         # 3. . -> pop(결과출력)
#         elif tok == '.':
#             if len(stack) != 1:
#                 return 'error'
#             else:
#                 return stack.pop()


T = int(input())
for tc in range(1, T+1):
    susik = input().split()    # 바로 후위연산식으로 받음

    stack = [0] * 100
    top = -1

    ans = 0
    for x in susik:
        if x not in '+-*/.':
            top += 1
            stack[top] = int(x)
        elif x == '.':
            if top != 0:
                ans = 'error'
                break
            top -= 1
            ans = stack[top + 1]
        else:
            if top <= 0:
                ans = 'error'
                break
            top -= 1
            op2 = stack[top+1]
            top -= 1
            op1 = stack[top+1]
            if x == '+':
                top += 1
                stack[top] = op1 + op2
            elif x == '-':
                top += 1
                stack[top] = op1 - op2
            elif x == '*':
                top += 1
                stack[top] = op1 * op2
            elif x == '/':
                top += 1
                stack[top] = op1 // op2

    print(f'#{tc} {ans}')


# # 강사님 풀이
#     code = list(map(str, input().split()))
#     print(f'#{tc} {forth(code)}')