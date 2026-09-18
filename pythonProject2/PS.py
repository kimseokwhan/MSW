# SW 문제해결 응용
######################################################################
#   start 1 (0918)

# 시간복잡도!!! = 기본연산 수행횟수 + 입력받는 데이터를 종합적으로 고려해서 계산하는 점근적 표기법

# a = 5
# b = 3
# c = 56
# print(a)
# print(b)                     # O(5) (빅오)

# n = int(input())
# for _ in range(n):
#     print('#')                 # O(n)

# n = int(input())
# m = int(input())
# for _ in range(n):
#     print('#')
# for _ in range(m):
#     print('@')                  # O(2n+2)

# n = int(input())
# m = int(input())
# for i in range(n):
#     for j in range(m):
#         print('##')                  # O(n**2)

# O(1) < O(logN) < O(N) < O(NlogN) < O(n**2) ...   시간 복잡도


######################################################################
#   start 2 (0918)

# 표준 입출력 방법
# import sys
# sys.stdin = open("input.txt", "r")
# sys.stdout = open("output.txt", "w")
# for _ in range(10):
#     tc = int(input())
#     arr = [list(map(int, input().split())) for _ in range(100)]
#     ans = 0
#     print(f'#{tc} {ans}')

# 진법과 연산
# # 진법
# a = 13      # 10진수
# b = bin(a)  # 2진수
# c = oct(a)  # 8진수
# d = hex(a)  # 16진수
# print(b, c, d)
# print(type(b))
# # 다시 10진수로 b,c,d 값을 바꿔보자
# print(int(b, 2))
# print(int(c, 8))
# print(int(d, 16))

# # 10진수 17을 3진수로 바꾸기
# a = 17
# trans=""
# while a != 0:
#     rest = a % 3
#     trans += str(rest)
#     a //= 3
# answer = trans[::-1]
# print(answer)
#
# result = int(answer, 3)     # 다시 10진수로
# print(result)

# # 비트 연산
# print(13&9)     # & empersand -> and
# print(13|9)     # | vertical bar -> or
# print(13^9)     # ^ caret -> xor (exclusive or)
# print(10<<2)
# print(10>>2)

# # 부분집합
# arr1 = [1,2,3]
# for i in range(1<<3):   # 부분집합의 개수만큼 반복 0 1 2 3 4 5 6 7
#     result = []
#     for index in range(3):      # index 0 1 2
#         if i & (1<<index) != 0:     # 결과값이 0이 아니라면 index번째 비트는 1이다
#             result.append(arr1[index])
#     print(result)
#
# # 부분집합 재귀
# arr2 = [1,2,3]
# def abc(level, path):
#     if level == 3:
#         print(*path)
#         return
#     abc(level+1, path)
#     abc(level + 1, path+[arr2[level]])
# abc(0, [])

# # 음수 표현 방법 (보수)
# # 1의 보수: 비트 뒤집기
# # 2의 보수: 1의 보수 + 1
# print(~4 + 1)
# print(~-4 + 1)

# # 컴퓨터는 이진수를 사용하기 때문에 정확한 실수 표현이 불가능 한 경우가 있다!!!
# from decimal import Decimal
# a = Decimal('1.2') - Decimal('1.1')
# print(a)
# a = 1.2 - 1.1
# print(a)
#
# a = 1.25
# print(f'{a:.1f}')
# a = 1.35
# print(f'{a:.1f}')
# # 파이썬은 반올림을 가까운 짝수 쪽으로 한다...
# print(round(4.5))
# print(round(5.5))
#
# # 객기
# # 1.25 를 정확하게!!! 표현하고 싶다!!!
# # 1.25 -> '1.25' -> . 빼버리기 -> 10으로 나누기 -> 출력할때 소수점 따로 출력하기
# a = 1.25
# a = str(a)
# a = int(a.replace(".", ''))     #125
# a = ((a+5)//10)
# print(a)
# print(f'{a//10}.{a%10}')