# SW 문제해결 응용(알고리즘 응용, PS)
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


######################################################################
#   컴퓨팅 사고력 (0928)

# # 항진명제 = 항상 참인 명제
# if x>10 or x<=10:
#     print("실행")
# # 모순명제 = 항상 거짓인 명제
# if x>10 and x<=10:
#     print("실행")


######################################################################
#   완전 탐색(검색)/그리디 1 (0929)

# # 재귀 연습
# n = int(input())
# path = [0]*n
# def abc(level):
#     if level==n:
#         print(*path)
#         return
#     for i in range(1,7):
#         path[level]=i
#         abc(level+1)
# abc(0)

# def kfc(test):
#     print(test)
#     print('!!')
#
# def abc(test):
#     print('#')
#     print(test)
#     kfc(456)
#     print('**')
#     print(test)
#
# def bbq():
#     abc(123)
#     print('@')
#
# bbq()   # 함수가 끝나면 그 함수를 호출한 곳으로 돌아간다

# def abc(level):
#     # print(level, end=' ')
#     if level==2:
#         return
#
#     abc(level+1)
#     print(level, end=' ')
#
# abc(0)

# 누적합 구하기 - 재귀 DFS 구현시 변수를 global 선언하는가? 매개변수에 선언하는가? 에 따른 차이
# # 전역변수
# arr = [1, 3, 5, 7]
# Sum = arr[0]
# def abc(level):
#     global Sum
#     if level==3:
#         print(Sum, end=' ')
#         return
#     Sum += arr[level+1]
#     abc(level+1)
#     Sum -= arr[level+1]
#     print(Sum, end=' ')
#
# abc(0)

# # 매개변수
# arr = [1, 3, 5, 7]
# def abc(level, Sum):
#     if level==3:
#         print(Sum, end=' ')
#         return
#     abc(level+1, Sum+arr[level+1])
#     print(Sum, end=' ')
#
# abc(0, arr[0])

# def abc(level):
#     if level == 2:  # 트리의 레벨
#         return
#
#     for i in range(2):  # 트리의 브랜치(가지)
#         abc(level+1)
#     # abc(level + 1)
#     # abc(level + 1)
#     # abc(level + 1)
#
# abc(0)

# def abc(level):
#     ########################
#     if level == 2:
#         ########################
#         return
#     ########################
#     for i in range(2):
#         ########################
#         abc(level+1)
#         ########################
#     ########################
#
# abc(0)

# 순열 연습 (순열/중복순열)
# # 중복 순열
# # level = 3
# # branch = 4
# card = 'ABCD'
# path = [""]*3   # 경로저장하는 배열의 크기는 = level
#
# def abc(level):
#     if level == 3:
#         for i in range(level):
#             print(path[i], end=' ')
#         print()
#         return
#
#     for i in range(4):
#         path[level]=card[i]
#         abc(level+1)
#         path[level] = 0     # 경로 지우기
#
# abc(0)

# n = int(input())
# path = [0] * n
# def abc(level):
#     if level == n:
#         print(*path)
#         return
#
#     for i in range(1, 7):
#         path[level] = i     # 내가 앞으로 들어갈 곳을 path 배열에 기록
#         abc(level + 1)
# abc(0)

# # 순열
# card = 'ABCD'
# path = [""] * 3     # level(depth) 크기
# used = [0] * 4      # branch 크기
# def abc(level):
#     if level==3:
#         print(*path)
#         return
#
#     for i in range(4):
#         if used[i] == 1: continue   # 방문한 적이 있는지 확인
#         used[i] = 1     # 방문체크
#         path[level] = card[i]   # 앞으로 들어갈 경로 적기
#         abc(level + 1)      # 다음 함수 들어가기
#         path[level] = 0     # 경로 적었던것 지우고
#         used[i] = 0     # 방문체크 해제
# abc(0)

# 완전 탐색(검색)     # 카드 5개에서 3개 뽑았을 때 합이 10인 경우 몇가지?
# branch = 5
# level = 3
# 누적합
# arr = [3, 4, 7, 1, 6]
# cnt = 0
#
# # 매개변수로
# # def abc(level, Sum):
# #     global cnt
# #     if Sum > 10:    # 가지치기
# #         return
# #     if level == 3:
# #         if Sum == 10:
# #             cnt += 1
# #         return
# #
# #     for i in range(5):
# #         abc(level + 1, Sum + arr[i])    # level 1씩 증가 / Sum 내가 앞으로 들어갈 가지 더하기
# #
# # abc(0, 0)   # level, Sum
# # 전역변수로
# Sum = 0
# def abc(level):
#     global cnt, Sum
#     if Sum > 10:    # 가지치기
#         return
#     if level == 3:
#         if Sum == 10:
#             cnt += 1
#         return
#
#     for i in range(5):
#         Sum += arr[i]
#         abc(level + 1)
#         Sum -= arr[i]
#
# abc(0)
# print(cnt)


######################################################################
#   완전 탐색(검색)/그리디 2 (0930)

# # 완전탐색으로 부분집합 구하기
# name = 'ABC'
# def abc(level, path):
#     if level == 3:
#         print(*path)
#         # print(path)
#         return
#     abc(level+1, path)
#     abc(level+1, path+[name[level]])
# abc(0, [])

# # Binary Counting
# arr = ['A', 'B', 'C','D','E']
# n = len(arr)
#
# for tar in range(1 << n):
#     answer = []
#     for i in range(n):
#         if tar & 1:     # if tar&0x1:
#             answer.append(arr[i])
#         tar >>= 1
#     if len(answer) >= 2:    # 최소 2명 이상이 카페에 간다면!!!
#         print(answer)

# 순열, 중복순열, 조합, 중복조합
# # 중복순열
# card = 'ABCD'
# path = [''] * 3     # 카드 묶음의 개수(뽑을 카드 개수)
# def abc(level):
#     if level == 3:
#         print(*path)
#         return
#     for i in range(4):
#         path[level] = card[i]
#         abc(level + 1)
#         path[level] = ''
# abc(0)

# # 순열
# card = 'ABCD'
# path = [''] * 3     # 카드 묶음의 개수(뽑을 카드 개수) (level)
# used = [0] * 4      # 선택할 수 있는 카드 종류의 개수 (branch)
# def abc(level):
#     if level == 3:
#         print(*path)
#         return
#     for i in range(4):
#         if used[i] == 1: continue
#         used[i] = 1
#         path[level] = card[i]
#         abc(level + 1)
#         path[level] = ''
#         used[i] = 0
# abc(0)

# # 조합
# card = 'ABCD'
# path = [''] * 3
# def abc(level, start):
#     if level == 3:
#         print(*path)
#         return
#     for i in range(start, 4):
#         path[level] = card[i]   # 내가 앞으로 들어갈 경로를 적고
#         abc(level + 1, i + 1)   # 다음 함수에 진입
#         path[level] = ''        # 함수 리턴 후, 적었던 경로를 지우기 (생략가능)
# abc(0, 0)

# # 중복조합
# card = 'ABCD'
# path = [''] * 3
# def abc(level, start):
#     if level == 3:
#         print(*path)
#         return
#     for i in range(start, 4):
#         path[level] = card[i]   # 내가 앞으로 들어갈 경로를 적고
#         abc(level + 1, i)       # 다음 함수에 진입
#         path[level] = ''        # 함수 리턴 후, 적었던 경로를 지우기 (생략가능)
# abc(0, 0)

# Greedy (탐욕 알고리즘)      ※ <=> DP (동적 계획법)
# # 동전 교환 문제!!!
# coin = [500, 50, 100, 10]
# target = 1110
# coin.sort(reverse = True)
# # [500, 100, 50, 10]
#
# cnt = 0     # 사용한 동전 개수
# for i in range(4):
#     temp = target//coin[i]
#     cnt += temp
#     target = target - (temp * coin[i])
# print(cnt)

# # 화장실 문제!!!
# poo = [15,30,50,10]
# poo.sort()  # 10 15 30 50
# Sum = 0
# for i in range(3, 0, -1):   # 대기인원
#     Sum += (i * poo[3-i])
# print(Sum)

# # Knapsack 문제       냅색 문제는 그리디로 해결할 수 없다. 완전탐색 or DP로 접근해야 한다.
# # Fractional Knapsack 문제!!!     Fractional Knapsack 문제는 그리디로 구할 수 있다.
# bag = 30
# salt = [(5, 50), (10, 60), (20, 140)]
# # 키로당 단가가 높은 순서로 sort
# salt.sort(key=lambda x:x[1]//x[0], reverse=True)    # 단위당 단가가 가장 높은것 우선순위!!!
# print(salt)     # [(5, 50), (20, 140), (10, 60)]
# total_value = 0     # 가방의 총 가치
# for weight, price in salt:
#     # 다 담을 수 있다면!
#     # 다 담을 수 없다면!   가방에 담을 수 있는 가치는 = 남은 가방무게 * 담는 물건의 단위당 단가
#     if bag >= weight:
#         bag -= weight   # 담은만큼 가방 무게 빼고
#         total_value += price    # 가방의 가치를 업데이트
#     else:
#         total_value += (bag * (price // weight))
#         bag = 0
#         break
# print(total_value)

# # lambda - 익명함수
# def Sum(a, b):
#     return a + b
# result = Sum(3, 4)
# print(result)
# result1 = (lambda a, b: a + b)(3, 5)
# print(result1)
# result2 = (lambda a, b: a + b)
# print(result2(3, 6))

# # sort      # 원본 값 바꿈
# # sorted    # 원본 값 안바꿈, sort한 값만 뱉음
# arr = [3,1,2,5,1,3,6,5,3,2,21,5]
# arr.sort(reverse = True)
# print(arr)
#
# arr1 = [3,1,2,5,1,3,6,5,3,2,21,5]
# def test(x):
#     return -x
# arr1.sort(key = test)
# print(arr1)
#
# arr2 = [3,1,2,5,1,3,6,5,3,2,21,5]
# arr2.sort(key = lambda x:-x)
# print(arr2)

# salt = [(5, 50), (10, 60), (20, 140)]
# # 1. 튜플의 1번 인덱스 기준으로 정렬
# salt.sort(key=lambda x:x[1], reverse=True)
# print(salt)
#
# salt1 = [(5, 50), (10, 60), (20, 140)]
# # 2. 단위당 단가가 가장 높은 순으로 (단위당 단가 = 가치 // 무게)
# salt1.sort(key=lambda x:x[1]//x[0], reverse=True)
# print(salt)


######################################################################
#   분할정복/백트래킹 1 (1001)

# # 병합 정렬 (Merge Sort)
# arr = [2, 3, 5, 7, 1, 2, 5, 9]
# start = 0
# end = 7
# mid = (start + end) // 2
#
# a = start
# b = mid + 1
# result = []
#
# while 1:
#     if a > mid and b > end: break
#     if a > mid:
#         result.append(arr[b])
#         b += 1
#     elif b > end:
#         result.append(arr[a])
#         a += 1
#     elif arr[a] <= arr[b]:
#         result.append(arr[a])
#         a += 1
#     else:
#         result.append(arr[b])
#         b += 1
# print(*result)

# arr = [2, 7, 5, 3, 1, 6, 9, 2]
# def merge(start, end):
#     if start == end:
#         return
#     mid = (start + end) // 2
#
#     merge(start, mid)
#     merge(mid + 1, end)
#
#     a = start
#     b = mid + 1
#     result = []
#
#     while 1:
#         if a > mid and b > end: break
#         if a > mid:
#             result.append(arr[b])
#             b += 1
#         elif b > end:
#             result.append(arr[a])
#             a += 1
#         elif arr[a] <= arr[b]:
#             result.append(arr[a])
#             a += 1
#         else:
#             result.append(arr[b])
#             b += 1
#     for i in range(len(result)):
#         arr[start + i] = result[i]
# merge(0, 7)
# print(*arr)

# # 퀵 정렬 (Quick Sort) - ############여기서부터 라이브 다시볼것
# '''
# rule: a는 pivot보다 큰수가 나올때까지 이동
#         b는 pivot보다 작거나 같은수 나올까까지 이동
#         둘이 엇갈렸다면 break
#         a,b 자리잡을땐
#         swap(a값, b값)
#         맨마지막에
#         swap(b값, pivot값)
# '''
# arr = [4, 7, 1, 6, 2, 8, 5, 3, 9]
# start = 0
# end = 8
# pivot = start
# a = start + 1
# b = end
# while 1:
#     while a <= end and arr[a] <= arr[pivot]: a += 1     # 배열 범위 안이고, a의 값이 pivot보다 작다면
#     while b >= start and arr[b] > arr[pivot]: b -= 1    # 배열 범위 안이고, b의 값이 pivot보다 크다면
#     if a > b: break
#     arr[a], arr[b] = arr[b], arr[a]
# arr[b], arr[pivot] = arr[pivot], arr[b]
# print(*arr)


######################################################################
#   분할정복/백트래킹 2 (1002)

'''
완전탐색(Brute Force) - 어디까지 탐색? (중복순열)
DFS - 탐색순서에 포커스 맞춰서 푼다
가지치기(Pruning) - 굳이 탐색할 필요가 없는 경우 탐색 안함
백트래킹 - 탐색 후 돌아옴 (취소)
'''
# # 백트래킹 - N-Queen
# # branch 4 // level 4
# # vertical = [j]
# # seven = [i+j]
# # five = [i-j+n]
#
# # N*N 사이즈의 체스판에 N개의 퀸을 방해 없이 놓을 수 있는 경우
# # 그 경우가 몇가지 인가요???  8 입력    92개
#
# n = int(input())    # 체스판 크기
# vertical = [0] * n
# seven = [0] * (2*n)
# five = [0] * (2*n)
#
# cnt = 0
# def abc(level):
#     global cnt
#     if level == n:
#         cnt += 1
#         return
#     for j in range(n):
#         if vertical[j] == 1: continue
#         if seven[level + j] == 1 or five[level - j + n] == 1: continue  # 가지치기
#         vertical[j], seven[level+j], five[level-j+n] = 1,1,1
#         abc(level+1)
#         vertical[j], seven[level + j], five[level - j + n] = 0,0,0  # 백트래킹 개념
# abc(0)
# print(cnt)

'''
자료구조? - 데이터를 어떻게 저장 또는 관리할 것인가??
        데이터를 저장하는 방식에 따라
        선형 자료구조: 리스트, Linked list(연결 리스트)
        비선형 자료구조: 그래프(트리)
'''
# # 연결 리스트 예시
# class Node:
#     def __init__(self, value):
#         self.value=value    # 인스턴스에 저장될 값
#         self.next=None      # 참조하고 있는 객체가 저장
#                             # 나 다음에는 너야!! 라는 정보
# a=Node(10)
# b=Node(20)
# c=Node(30)
# a.next=b
# b.next=c
#
# head=a
# while head:
#     print(head.value)
#     head=head.next


######################################################################
#   그래프 1 (1006)

# # DFS (인접 행렬) = 가능한 모든 정점 1번씩 탐색
# # 1번 인덱스부터 DFS 탐색 순서 출력 (1번씩 탐색)
# name = 'BACD'
# arr = [[0,0,1,1],
#        [1,0,1,0],
#        [1,0,0,1],
#        [0,0,0,0]]
# used = [0] * 4    # 정점의 개수만큼 방문체크
# def dfs(now):
#     print(name[now], end=' ')
#     for i in range(4):
#         if arr[now][i] == 1 and used[i] == 0:
#             used[i] = 1
#             dfs(i)
# used[1] = 1    # 탐색 시작 인덱스에 1 중복 체크
# dfs(1)  # 탐색 시작 인덱스

# # DFS (인접 리스트) = 가능한 모든 정점 1번씩 탐색
# '''
# 4 6
# 0 2
# 0 3
# 1 0
# 1 2
# 2 0
# 2 3
# '''
# name = 'BACD'
# n, m = map(int, input().split())    # 정점, 간선 정보의 개수
# arr = [[] for _ in range(n)]
# for _ in range(m):
#     start, end = map(int, input().split())
#     arr[start].append(end)
# used = [0] * n    # 정점의 개수만큼 방문체크
# def dfs(now):
#     print(name[now], end=' ')
#     for i in arr[now]:
#         if used[i] == 0:
#             used[i] = 1
#             dfs(i)
# used[1] = 1    # DFS 시작 인덱스에 1 체크
# dfs(1)

# # DFS (인접 리스트) = 한 정점에서 다른 정점까지의 도착할 수 있는 방법이 몇가지?
# '''
# 4 6
# 0 2
# 0 3
# 1 0
# 1 2
# 2 0
# 2 3
# '''
# name = 'BACD'
# n, m = map(int, input().split())    # 정점, 간선 정보의 개수
# arr = [[] for _ in range(n)]
# for _ in range(m):
#     start, end = map(int, input().split())
#     arr[start].append(end)
# used = [0] * n    # 정점의 개수만큼 방문체크
# cnt = 0
# def dfs(now):
#     global cnt
#     if now == 3:    # if name[now] == 'D':
#         cnt += 1
#     for i in arr[now]:
#         if used[i] == 0:
#             used[i] = 1
#             dfs(i)
#             used[i] = 0
# used[1] = 1    # DFS 시작 인덱스에 1 체크
# dfs(1)
# print(cnt)

# # BFS 너비우선 탐색 (모든 정점을 한번씩 탐색)
# '''
# 4 6
# 0 1
# 0 2
# 1 2
# 1 3
# 2 1
# 2 3
# '''
# from collections import deque
# n, m = map(int, input().split())
# arr = [[] for _ in range(n)]
# for _ in range(m):
#     a, b = map(int, input().split())
#     arr[a].append(b)
# q = deque()
# used = [0] * n
# q.append(0)     # 시작점 큐에 넣기
# used[0] = 1     # 시작점 방문체크
# name = 'ABCD'
# while q:
#     now = q.popleft()   # 큐에 있는것 빼기
#     print(name[now], end=' ')
#     for i in arr[now]:      # 이동 가능한것 탐색
#         if used[i] == 0:    # 방문여부 확인
#             used[i] = 1     # 방문체크
#             q.append(i)     # 큐에 넣기

# # Union-Find 자료구조 - 각각의 독립된 data를 그룹화 해서 관리
# # arr = [i for i in range(6)]
# # print(arr)
# arr = [0, 1, 2, 3, 4, 5]
# rank = [0] * 6
#
# def findboss(member):
#     if arr[member] == member:   # 자기 자신이 보스라면 (그 그룹의 보스 찾음)
#         return member
#     ret = findboss(arr[member]) # 보스가 아니라면 arr배열의 값을 가지고 보스 찾기
#     arr[member] = ret   # 경로 단축 (중요!!!@@@)
#     return ret
#
# def union(a, b):
#     fa = findboss(a)
#     fb = findboss(b)
#     if fa == fb:    # 두 보스가 같으면 이미 같은 그룹
#         return
#     # arr[fb] = fa    # 보스가 다르면 a의 보스가 통합 장
#     if rank[a] == rank[b]:
#         rank[a] += 1
#         arr[fb] = fa
#     elif rank[a] > rank[b]:
#         arr[fb] = fa
#     else:
#         arr[fa] = fb
#
# union(0,1)
# union(3,4)
# union(1,4)
# union(1,3)
# union(5,4)
#
# y,x = map(int, input().split())     # 숫자 2개 입력 후 같은 그룹인지 출력
# if findboss(y) == findboss(x):
#     print('이미 같은 그룹')
# else:
#     print('다른 그룹')


######################################################################
#   그래프 2 (1007)

# 우선순위 큐
# # min heap
# import heapq
# arr = []
# heapq.heappush(arr, 13)
# heapq.heappush(arr, 5)
# heapq.heappush(arr, 17)
# heapq.heappush(arr, 9)
# print(arr)
# # for i in range(len(arr)):
# #     print(heapq.heappop(arr), end=' ')
# while arr:
#     node = heapq.heappop(arr)
#     print(node, end=' ')

# # max heap
# import heapq
# arr = [3, 234, 23, 12, 31]
# heap = []
# for i in range(len(arr)):
#     heapq.heappush(heap, -arr[i])
# for i in range(len(arr)):
#     # print(heapq.heappop(heap) * -1, end=' ')
#     print(-heapq.heappop(heap), end=' ')
#
# # heapify 사용 (시간 줄임)
# import heapq
# arr = [3, 234, 23, 12, 31]
# arr = list(map(lambda x:-x, arr))   # arr 배열의 모든 원소에 - 붙인후, arr에 재핳당
# heapq.heapify(arr)
# for i in range(len(arr)):
#     print(-heapq.heappop(arr), end=' ')

# # prim 알고리즘
# import heapq
#
# n = int(input())
# m = int(input())
#
# arr = [[] for _ in range(n)]
#
# # 무방향 그래피이므로 양방향 저장
# for _ in range(m):
#     start, end, cost = map(int, input().split())
#
#     arr[start].append((cost, end))
#     arr[end].append((cost, start))
#
# used = [0] * n
# heap = []
#
# # (비용, 정점)
# heapq.heappush(heap, (0, 0))    # 비용 시작정점
#
# total = 0   # 총 비용을 합치기
# cnt = 0     # 연결한 간선의 개수
#
# while heap:
#     cost, now = heapq.heappop(heap)
#
#     # 이미 MST에 포함된 정점이면 무시
#     if used[now] == 1:
#         continue
#
#     # MST에 정점 포함
#     used[now] = 1   # 방문체크
#     total += cost   # 비용의 합
#     cnt += 1        # 연결된 간선의 개수 1증가
#
#     # 모든 정점을 선택했다면 종료
#     if cnt == n:
#         break
#
#     # 현재 정점과 연결된 간선들을 우선순위 큐에 추가
#     for next_cost, next_node, in arr[now]:
#         if used[next_node] == 0:
#             heapq.heappush(heap, (next_cost, next_node))
#
# print(total)

# kruskal 알고리즘      ####################다시보기
