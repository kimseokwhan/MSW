import sys
sys.stdin = open("bracket_check_input.txt")


# # 강사님 풀이
# def solve(text):
#     stack = []
#     # 1. 문자열을 하나씩 순회
#     for i in range(len(text)):
#         # 2. 왼쪽괄호 -> push
#         if text[i] == '(' or text[i] == '{':    # text[i] in '({'
#             stack.append(text[i])
#         # 3. 오른쪽괄호 -> pop
#         elif text[i] in ')}':
#             # 3.1 isEmpty
#             if len(stack) == 0:     # if not stack:
#                 return 0
#             # 3.2 pop
#             else:
#                 temp = stack.pop()
#                 # 3.3 짝검사
#                 if text[i] == ')' and temp != '(':
#                     return 0
#                 elif text[i] == '}' and temp != '{':
#                     return 0
#                 # elif text[i] == ']' and temp != '[':
#                 #     return 0
#     # 4. isEmpty
#     if len(stack) != 0:
#         return 0
#
#     return 1


T = int(input())
for tc in range(1, T+1):
    # txt = list(map(str, input()))
    text = input()

    # print(txt)
    # print(text)

    pair = {'}': '{', ')': '('}
    # 스택 생성
    top = -1
    stack = [0] * 100

    ans = 1
    for x in text:
        if x in '{(':
            top += 1
            stack[top] = x
        elif x in '})':
            if top == -1:
                ans = 0
                break
            else:
                top -= 1
                tmp = stack[top+1]
                if pair[x] != tmp:
                    ans = 0
                    break
    if top != -1:
        ans = 0

    print(f'#{tc} {ans}')


# # 강사님 풀이
#     print(f'#{tc} {solve(text)}')