######################################################################
#   LIST 2-1 (0902)

# arr = [
#     [1, 2, 3],
#     [4, 5, 6, 7]
# ]
#
# print(arr)
# print(len(arr))
# print(len(arr[0]), len(arr[1]))
#
# for i in range(len(arr)):
#     for j in range(len(arr[i])):
#         print(arr[i][j])

# N, M = map(int, input().split())
# arr = [list(map(int, input().split())) for _ in range(N)]
# s = 0
#
# # 행 우선 선회
# for i in range(N):
#     for j in range(M):
#         s += arr[i][j]
#
# print(s)

# # 열 우선 선회
# for j in range(m):
#     for i in range(n):
#         f(array[i][j])    # 필요한 연산 수행

# # 지그재그 순회
# for i in range(n):
#     for j in range(m):
#         f(array[i][j + (m-1-2*j) * (i%2)])


# # 델타(네방향 탐색)
# for i in range(N):
#     for j in range(M):
#         for di, dj in [[0,1],[1,0],[0,-1],[-1,0]]:
#             ni, nj = i+di, j+dj ...

# # 연습 문제 1
# N = int(input())
# arr = [list(map(int, input().split())) for _ in range(N)]
#
# ans = 0
# for i in range(N):
#     ans += arr[i][i] + arr[i][N-1-i]
# if N%2:     # N이 홀수인 경우에만 중심 원소가 겹침
#     ans -= arr[N//2][N//2]
# print(ans)

# # 연습 문제 2
# N = int(input())
# arr = [list(map(int, input().split())) for _ in range(N)]
#
# total = 0
# for i in range(N):
#     for j in range(N):
#         s = 0   # i, j 이웃과 차이의 절댓값의 합
#         for di, dj in [[0,1],[1,0],[0,-1],[-1,0]]:
#             ni, nj = i + di, j + dj # 이웃 원소 인덱스 후보
#             if 0<=ni<N and 0<=nj<N: # 존재하는 인덱스면
#                 s += abs(arr[i][j] - arr[ni][nj])
#         total += s
# print(total)


######################################################################
#   LIST 2-2 (0903)

# # 비트 연산으로 부분집합을 생성하는 방법
# arr = [3, 6, 7, 1, 5, 4]
# n = len(arr)
#
# for i in range(1<<n):
#     for j in range(n):
#         if i & (1<<j):
#             print(arr[j], end=", ")
#     print()
# print()

# # 연습 문제 3
# arr = [-7, -5, 2, 3, 8, -2, 4, 6, 9, 12]
# N = len(arr)
#
# ans = 'N'
# for i in range(1, 1<<N):   # 2**N, 부분집합을 표현할 비트 생성
#     s = 0
#     for J in range(N):  # 검사할 비트 번호 j
#         if(i & (1<<j)): # j번 비트가 1이면 arr[j]가 부분집합의 원소
#             s += arr[j]
#     if s == 0:
#         ans = 'Y'
#         break   # for i
# print(ans)

# # 순차 검색 (정렬되어 있지 않은 경우)
# def sequential_search(a, n, key):
#     for i in range(n):
#         if a[i] == key:
#             return i
#     return -1
# # while 문 활용
# def sequential_search(a, n, key):
#     i = 0
#     while i < n and a[i] != key:
#         i += 1
#     if i < n:
#         return i
#     else:
#         return -1

# # 순차 검색 (정렬되어 있는 경우)
# def sequential_search2(a, n, key):
#     for i in range(n):
#         if a[i] == key:
#             return i
#         elif a[i] > key:
#             return -1
#     return -1
# # while 문 활용
# def sequential_search2(a, n, key):
#     i = 0
#     while i < n and a[i] < key:
#         i += 1
#     if i < n and a[i] == key:
#         return i
#     else:
#         return -1

# # 이진 검색 - ※ 이진 검색을 하기 위해서는 자료가 정렬된 상태여야 함 (중요)
# def binary_search(a, N, key):
#     start = 0
#     end = N-1
#     while start <= end:
#         middle = (start + end)//2
#         if a[middle] == key:
#             return middle
#         elif a[middle] > key:
#             end = middle - 1
#         else:
#             start = middle + 1
#     return -1

# # 선택 정렬
# def selection_sort(a, N):   # 오름차순
#     # 구간 정하기
#     for i in range(N-1):
#         # 구간의 최솟값 위치 찾기
#         min_idx = i     # 구간의 첫 원소를 최소로 가정
#         for j in range(i+1, N):
#             if a[min_idx] > a[j]:
#                 min_idx = j
#         # 구간의 맨 앞 원소와 최솟값 교환
#         a[i], a[min_idx] = a[min_idx], a[i]
#     return
# arr = [7, 2, 3, 5, 4]
# selection_sort(arr, len(arr))
# print(arr)

# # 셀렉션 알고리즘 - k 번째로 작은 원소를 찾는 알고리즘
# def select(arr, k):
#     for i in range(0, k):
#         min_idx = i
#         for j in range(i+1, len(arr)):
#             if arr[min_idx] > arr[j]:
#                 min_idx = j
#         arr[i], arr[min_idx] = arr[min_idx], arr[i]
#     return arr[k-1]


######################################################################
#   String 1 (0907)

# # String_ex1
# s1 = input()
# s2 = input()
# # 모두 있다고 가정하고, 하나라도 없으면
# # 'NO'로 바꾸고 종료
# ans = 'YES'
# for ch in s1:
#     if ch not in s2:
#         ans = 'NO'
#         break   # for ch
# print(ans)

# # String_ex2
# N = int(input())
# txt = [input() for _ in range(N)]
#
# ans = 'NO'
# for row in txt:
#     if 'Z' in row:
#         ans = 'YES'
#         break   # for row
# print(ans)
#
# def find_Z(txt, N):
#     for i in range(N):  # 2중 for문
#         for j in range(N):
#             if txt[i][j] == 'Z':
#                 return "YES"
#     return "NO"
# z = find_Z(txt, N)
# print(z)
# print(find_Z(txt, N))

# # String_ex3
# N = int(input())
# txt = [input() for _ in range(N)]
#
# cnt = 0
# for i in range(N):
#     for j in range(N):
#         if txt[i][j] == '#':
#             cnt += 1
# print(cnt)

# # String_ex4
# def find_pat(text, N):
#     pat = ['AB', 'CD']
#     for i in range(N-1):    # 기준위치 i, j
#         for j in range(N-1):
#             cnt = 0
#             for r in range(2):
#                 for c in range(2):
#                     if text[i+r][j+c] == pat[r][c]:
#                         cnt += 1
#             if cnt == 4:
#                 return 'YES'
#     return 'NO'
#
# N = int(input())
# text = [input() for _ in range(N)]
#
# print(find_pat(text, N))

# # String_ex5
# N = int(input())
# text = [input() for _ in range(N)]
#
# ans = 0     # 4방향이 모두 통로인 칸 수
# for i in range(N):
#     for j in range(N):
#         if text[i][j] != '1':   # 벽이 아니면
#             cnt = 0     # 현재 위치에서 주변 통로 개수
#             for di, dj in [[0,1],[1,0],[0,-1],[-1,0]]:
#                 ni = i + di
#                 nj = j + dj
#                 if 0<=ni<N and 0<=nj<N:
#                     if text[ni][nj] != '1':
#                         cnt += 1
#             if cnt == 4:
#                 ans += 1
# print(ans)


######################################################################
#   String 2 (0907)


######################################################################
#   Stack 1-1 (0908)

# # 스택 구현
# stack = [0] * 10
# top = -1
#
# top += 1
# stack[top] = 1  # push(1)
# top += 1
# stack[top] = 2  # push(2)
# top += 1
# stack[top] = 3  # push(3)
#
# top -= 1
# print(stack[top + 1])   # pop()
# top -= 1
# print(stack[top + 1])
# top -= 1
# print(stack[top + 1])

# # 괄호 검사
# txt = input()
# # 스택 생성
# top = -1
# stack = [0] * 100
#
# ans = 1
# for x in txt:
#     if x == '(':    # 여는 괄호면 push
#         top += 1
#         stack[top] = x
#     elif x == ')':  # 닫는 괄호면 꺼내서 확인
#         if top == -1:   # 스택이 비어있으면 오류(여는 괄호 부족)
#             ans = 0
#             break   # for x
#         else:   # 짝이 맞는지 확인하기...
#             top -= 1
# if top != -1:   # 여는 괄호가 더 많은 경우
#     ans = 0
#
# print(ans)

# # 괄호 검사 (중괄호 포함)
# txt = input()
# pair = {')':'(', '}':'{'}
#
# # 스택 생성
# top = -1
# stack = [0] * 100
#
# ans = 1
# for x in txt:
#     if x in '{(':    # 여는 괄호면 push
#         top += 1
#         stack[top] = x
#     elif x in ')}':  # 닫는 괄호면 꺼내서 확인
#         if top == -1:   # 스택이 비어있으면 오류(여는 괄호 부족)
#             ans = 0
#             break   # for x
#         else:   # 짝이 맞는지 확인하기...
#             top -= 1
#             tmp = stack[top + 1]    # pop
#             if pair[x] != tmp:  # x의 짝(여는 괄호)과 스택에서 꺼낸 여는 괄호가 다르면...
#                 ans = 0
#                 break   # for x
#
# if top != -1:   # 여는 괄호가 더 많은 경우
#     ans = 0
#
# print(ans)


######################################################################
#   Stack 1-2 (0909)

# # 재귀 구현
# def f(i, N):    # 배열의 모든 원소를 출력하는 함수, i 인덱스, N 배열 크기
#     if i == N:
#         return
#     else:
#         # print(A[i])
#         f(i+1, N)
#         print(A[i])
#
# A = [1,2,3]
# f(0, 3)

# # 피보나치 수열
# def fibo(n):
#     global cnt
#     cnt += 1
#     if n < 2:
#         return n
#     else:
#         return fibo(n-1) + fibo(n-2)
#
# cnt = 0
# print(fibo(10), cnt)

# # Memoization을 적용한 피보나치
# def fibo1(n):
#     global cnt
#     cnt += 1
#     if n >= 2 and memo[n] == 0:
#         memo[n] = fibo1(n-1)+fibo1(n-2)
#     return memo[n]
#
# n = 10
# cnt = 0
# memo = [0] * (n+1)
# memo[0] = 0
# memo[1] = 1

# # fibo_dp
# def fibo2(n) :
#     f = [0] * (n + 1)
#     f[0] = 0
#     f[1] = 1
#     for i in range(2, n + 1) :
#         f[i] = f[i-1] + f[i-2]
#
#     return f[n]
#
# print(fibo2(10))

# DFS (※ Advanced)
'''
7 8
1 2 1 3 2 4 2 5 4 6 5 6 6 7 3 7
'''
# def dfs(v):
#     print(v)
#     visited[v] = 1
#     # v에 인접하고 방문 안한 w
#     for w in adj_list[v]:   # 저장한 순서대로...
#         if visited == 0:    # 방문 안한곳
#             dfs(w)
#
# V, E = map(int, input().split())
# graph = list(map(int, input().split()))
# adj_list = [[] for _ in range(V+1)]
# for i in range(E):
#     v, w = graph[i*2], graph[i*2+1]
#
#     adj_list[v].append(w)
#     adj_list[w].append(v)   # 방향이 없는 경우 추가
#
# visited = [0] * (V+1)
# dfs(1)

# # 그래프 표현방법: 인접리스트, 순회: DFS (강사님 예시)
# def dfs(v):
#     # 1. 시작정점을 방문체크
#     visited[v] = 1
#     print(v, end=' ')
#     # 2. 시작정점(v)에 인접한 정점(w)이 미방문 시 -> dfs(w)
#     for w in adj_lst[v]:
#         if visited[w] == 0:
#             dfs(w)
#
# V, E = map(int, input().split())
# temp = list(map(int, input().split()))
# # 인접리스트 초기화
# adj_lst = [[] for _ in range(V+1)]
# # 방문체크
# visited = [0] * (V+1)
# # 인접리스트에 저장
# for i in range(E):
#     s, e = temp[2*i], temp[2*i+1]
#     adj_lst[s].append(e)
#     adj_lst[e].append(s)
#
# dfs(1)


######################################################################
#   Stack 2-1 (0910)

# # 후위 표기법으로 변환
# '''
# (6+5*(2-8)/2)
# 6528-*2/+
# '''
# icp = {'(':3, '*':2, '/':2, '+':1, '-':1}   # in-comming priority
# isp = {'(':0, '*':2, '/':2, '+':1, '-':1}   # in-stack priority
# stack = [0] * 100
# top = -1
#
# fx = '(6+5*(2-8)/2)'
# susik = ''  # 후위 연산식 기록할 빈 문자열
#
# for x in fx:
#     if x not in '(+-*/)':   # 피연산자인 경우 출력
#         susik += x
#     elif x == ')':  # 여는 괄호까지 pop
#         while stack[top] != '(':    # peek
#             top -= 1
#             susik += stack[top+1]
#         top -= 1    # 남아있는 '(' 버림
#     else:   # 연산자인 경우
#         if top == -1 or icp[x] > isp[stack[top]]:   # icp > top원소 isp : push
#             top += 1
#             stack[top] = x
#         else:   # icp <= isp : icp > isp까지 pop
#             while top > -1 and isp[stack[top]] >= icp[x]:
#                 top -= 1
#                 susik += stack[top+1]
#             top += 1    # push x
#             stack[top] = x
# print(susik)
#
# # 후위 표기법 연산
# for x in susik:
#     if x not in '+-*/': # 피연산자면 push
#         top += 1
#         stack[top] = int(x)
#     else:   # 연산자면
#         # 피연산자 두개를 꺼내서 ...
#         top -= 1
#         op2 = stack[top+1]  # 오른쪽 피연산자
#         top -= 1
#         op1 = stack[top + 1]  # 오른쪽 피연산자
#         if x == '+':    # 연산결과를 push
#             top += 1
#             stack[top] = op1 + op2
#         elif x == '-':    # 연산결과를 push
#             top += 1
#             stack[top] = op1 - op2
#         elif x == '*':    # 연산결과를 push
#             top += 1
#             stack[top] = op1 * op2
#         elif x == '/':    # 연산결과를 push
#             top += 1
#             stack[top] = op1 / op2
#
# top -= 1
# ans = stack[top+1]
# print(ans)


######################################################################
#   Stack 2-2 (0911)

# # 가지치기 부분집합
# def f(i, k, s, t):  # i원소, k 집합의 크기, s i-1까지 고려된 합, t목표
#     global cnt
#     global fcnt
#     fcnt += 1
#     if s > t:   # 고려한 원소의 합이 찾는 합보다 큰경우
#         return
#     elif s == t:    # 남은 원소를 고려할 필요가 없는 경우
#         cnt += 1
#         return
#     elif i == k:    # 모든원소 고려
#         return
#     else:
#         bit[i] = 1
#         f(i+1, k, s+A[i], t)    # A[i] 포함
#         bit[i] = 0
#         f(i+1, k, s, t)         # A[i] 미포함
#
# #A = [1,2,3,4,5,6,7,8,9,10]
# N = 10
# A = [ i for i in range(1, N+1)]
#
# key = 55
# cnt = 0
# bit = [0]*N
# fcnt = 0
# f(0,N,0,key)
# print(cnt, fcnt)      # 합이 key인 부분집합의 수

# # 순열2
# def f(i, N):
#     if i == N:
#         print(p)
#     #     return
#     # for ~     # if 에서 return 하고 그 뒤 for ~ 하거나 else 로
#     else:
#         for j in range(i, N):
#             p[i], p[j] = p[j], p[i]
#             f(i  +1, N)
#             p[i], p[j] = p[j], p[i]
#
# p = [1, 2, 3, 4, 5]
# N = 5
# f(0, N)

# # 강사님 부분집합
# def powerset(lev):
#     # 1. 기본파트
#     if lev == N:
#         print(bit)
#         return
#     # 2. 유도파트
#     else:
#         bit[lev] = 1
#         powerset(lev+1)
#         bit[lev] = 0
#         powerset(lev + 1)
#
# arr = [1, 2, 3]
# N = len(arr)
# bit = [0] * N
# powerset(0)

# # 강사님 부분집합_가지치기
# # 부분집합의 합이 10인 경우
# def powerset(lev, cursum):
#     global cnt
#     cnt += 1
#
#     # 0. 가지치기
#     if cursum > 10: return
#
#     # 1. 기본파트
#     if lev == N:
#         if cursum == 10:
#             for i in range(N):
#                 if bit[i] == 1:
#                     print(arr[i], end=' ')
#             print()
#     # 2. 유도파트
#     else:
#         bit[lev] = 1
#         powerset(lev+1, cursum + arr[lev])
#         bit[lev] = 0
#         powerset(lev+1, cursum)
#
# arr = [i+1 for i in range(10)]      # list(range(1, 11))
# N = len(arr)
# bit = [0] * N
# cnt = 0
# powerset(0, 0)
# print(cnt)

# # 강사님 순열
# def perm(lev):
#     if lev == N:
#         print(path)
#     else:
#         for i in range(lev, N):
#             path[lev], path[i] = path[i], path[lev]
#             perm(lev+1)
#             path[lev], path[i] = path[i], path[lev]
#
# path = [1, 2, 3]
# N = len(path)
# perm(0)

# def perm(lev, cursum):
#     if lev == N:
#         print(path)
#     else:
#         for i in range(lev, N):
#             path[lev], path[i] = path[i], path[lev]
#             perm(lev+1, cursum + arr[lev][path[lev]])
#             path[lev], path[i] = path[i], path[lev]
#
# path = [1, 2, 3]
# N = len(path)
# perm(0, 0)


######################################################################
#   Queue 1 (0916)

# que = [0] * 1000000
# front = rear = - 1

# for i in range(1000000):
#     rear += 1
#     que[rear] = i
# print(rear)

# rear += 1   # enqueue(1)
# que[rear] = 1
# rear += 1   # enq 2
# que[rear] = 2
# rear += 1   # enq 3
# que[rear] = 3

# front += 1
# print(que[front])
# front += 1
# print(que[front])
# front += 1
# print(que[front])

# while front != rear:
#     front += 1
#     print(que[front])

# q = []  # 큐 생성
# q.append(1)
# q.append(2)
# q.append(3)
# print(q.pop(0))
# print(q.pop(0))
# print(q.pop(0))

# from collections import deque
# q = deque()     # 큐 생성
# for i in range(1000000):
#     q.append(i)
# print(len(q))
# for _ in range(1000000):
#     q.popleft()
# print(len(q))


######################################################################
#   Queue 2 (0916)

# # BFS
# '''
# 7 8
# 4 2 1 2 1 3 5 2 4 6 5 6 6 7 3 7
# '''
# def bfs(s, V):
#     # 초기화
#     visited = [0] * (V + 1)      # visited 생성
#     q = [s]                     # 큐 생성
#     # q.append(s)                 # 시작점 인큐
#     visited[s] = 1              # 시작점 인큐 표시
#     while q:
#         t = q.pop(0)        # 디큐
#         print(t)            # t 처리
#         for w in adj_l[t]:  # 인접하고 인큐된적이 없는 정점 w면
#             if visited[w] == 0:
#                 q.append(w) # 인큐하고 인큐 표시
#                 visited[w] = visited[t] + 1
#     print(visited)
#     # 반복
#
# V, E = map(int, input().split())
# arr =list(map(int, input().split()))
# # 인접리스트
# adj_l = [[] for _ in range(V + 1)]  # V번 행까지 필요
# for i in range(E):
#     v1, v2 = arr[i*2], arr[i*2+1]
#     adj_l[v1].append(v2)
#     adj_l[v2].append(v1)    # 방향이 없는 간선의 경우
#
# bfs(4, V)

# # BFS (출발점 두개)
# '''
# 7 8
# 4 2 1 2 1 3 5 2 4 6 5 6 6 7 3 7
# '''
# def bfs(s, V):
#     # 초기화
#     visited = [0] * (V + 1)      # visited 생성
#     q = [1, 4]                     # 큐 생성
#     # q.append(s)                 # 시작점 인큐
#     visited[1] = 1              # 시작점 인큐 표시
#     visited[4] = 1
#     while q:
#         t = q.pop(0)        # 디큐
#         print(t)            # t 처리
#         for w in adj_l[t]:  # 인접하고 인큐된적이 없는 정점 w면
#             if visited[w] == 0:
#                 q.append(w) # 인큐하고 인큐 표시
#                 visited[w] = visited[t] + 1
#     print(visited)
#     # 반복
#
# V, E = map(int, input().split())
# arr =list(map(int, input().split()))
# # 인접리스트
# adj_l = [[] for _ in range(V + 1)]  # V번 행까지 필요
# for i in range(E):
#     v1, v2 = arr[i*2], arr[i*2+1]
#     adj_l[v1].append(v2)
#     adj_l[v2].append(v1)    # 방향이 없는 간선의 경우
#
# bfs(1, V)

# # BFS를 활용한 미로 탐색 (swea 5105)
# def find_start(maze, N):
#     for i in range(N):
#         for j in range(N):
#             if maze[i][j] == '2':
#                 return i, j
#
# def bfs(i, j, N):
#     # 초기화
#     visited = [[0]*N for _ in range(N)]     # visited 생성
#     q = [(i, j)]                            # 큐 생성
#     # 시작점 인큐
#     visited[i][j] = 1                       # 시작점 인큐 표시
#     # 반복
#     while q:
#         ti, tj = q.pop(0)                   # 디큐
#         if maze[ti][tj] == '3':             # 처리
#             return visited[ti][tj] - 2
#         for di, dj in [[0,1],[1,0],[0,-1],[-1,0]]:  # 인접칸이 벽이 아니고 인큐한 적이 없으면
#             ni, nj = ti + di, tj + dj
#             if 0 <= ni < N and 0 <= nj < N and maze[ni][nj] != '1' and visited[ni][nj] == 0:
#                 q.append([ni, nj])          # 인큐, 인큐 표시
#                 visited[ni][nj] = visited[ti][tj] + 1
#     return 0
#
# T = int(input())
# for tc in range(1, T+1):
#     N = int(input())
#     maze = [input() for _ in range(N)]
#
#     si, sj = find_start(maze, N)
#     ans = bfs(si, sj, N)
#     print(f'#{tc} {ans}')

# # 물놀이를 가자 (swea 10966)
# from collections import deque
# N, M = map(int, input().split())
# arr = [input() for _ in range(N)]
#
# # 초기화
# visited = [[0] * M for _ in range(N)]
# q = deque()
# # 시작점 인큐 / 인큐 표시
# for i in range(N):
#     for j in range(M):
#         if arr[i][j] == 'W':
#             q.append((i,j))
#             visited[i][j] = 1
# # 반복
# while q:
#     ti, tj = q.popleft()
#     for di, dj in [[0,1],[1,0],[0,-1],[-1,0]]:  # 인접칸이 땅이고 방문한적 없으면
#         ni, nj = ti + di, tj + dj
#         if 0 <= ni < N and 0 <= nj < M and arr[ni][nj] == 'L' and visited[ni][nj] == 0:
#             q.append((ni, nj))
#             visited[ni][nj] = visited[ti][tj] + 1
#
# s = 0
# for row in visited:
#     s += sum(row)
# print(s - N*M)


######################################################################
#   Tree 1 (0917)

# '''
# 완전이진트리에서 11번 정점의 조상노드의 번호는?
# '''
# n = 11
# while n//2 > 0:
#     n //= 2
#     print(n)

# # 트리 ex
# def pre_order(T):   # 전위순회, 방문한 정점(부모) 먼저 처리
#     if T:   # 0이 아니면 (존재하는 정점이면)
#         print(T)    # visit(T) T에서 할일 처리
#         pre_order(left[T])  # 왼쪽 자식(서브트리)로 이동
#         pre_order(right[T]) # 오른쪽 자식(서브트리)로 이동
#
# def in_order(T):
#     if T:   # 0이 아니면 (존재하는 정점이면)
#         in_order(left[T])  # 왼쪽 자식(서브트리)로 이동
#         print(T)  # visit(T) T에서 할일 처리
#         in_order(right[T]) # 오른쪽 자식(서브트리)로 이동
#
# def post_order(T):
#     if T:   # 0이 아니면 (존재하는 정점이면)
#         post_order(left[T])  # 왼쪽 자식(서브트리)로 이동
#         post_order(right[T]) # 오른쪽 자식(서브트리)로 이동
#         print(T)  # visit(T) T에서 할일 처리
#
# N = int(input())    # 1번부터 N번 정점이 존재
# E = N -1            # 간선 수
# arr = list(map(int, input().split()))
#
# # 부모를 인덱스로 자식번호 저장
# left = [0] * (N + 1)    # N번 인덱스 필요
# right = [0] * (N + 1)
# for i in range(E):
#     p, c = arr[i*2], arr[i*2+1]
#     if left[p] == 0:
#         left[p] = c
#     else:
#         right[p] = c
#
# pre_order(1)


######################################################################
#   Tree 2 (0917)

# # subtree
# def pre_order(T):
#     global cnt
#     if T:
#         cnt += 1
#         pre_order(left[T])
#         pre_order(right[T])
#
# def f(T):
#     if T == 0:
#         return 0
#     l = f(left[T])
#     r = f(right[T])
#     return l + r + 1
#
# T = int(input())
# for tc in range(1, T+1):
#     # 간선의 개수 E, 서브트리 루트 N
#     E, N = map(int, input().split())
#     V = E + 1   # 마지막 정점 번호
#     arr = list(map(int, input().split()))
#
#     left = [0] * (V + 1)
#     right = [0] * (V + 1)
#
#     for i in range(E):
#         p, c = arr[i*2], arr[i*2+1]
#         if left[p] == 0:
#             left[p] = c
#         else:
#             right[p] = c
#
#     cnt = 0
#     pre_order(N)
#     ans = f(N)
#     print(f'#{tc} {cnt}')
#     print(f'#{tc} {ans}')

# # binary heap
# def enq(n):
#     global last
#     last += 1   # 마지막 정점 추가
#     heap[last] = n  # 마지막 정점에 저장
#
#     # 최소힙 : 부모 < 자식
#     c = last
#     p = c//2
#     # 부모가 있고, 부모 > 자식 이면 교환
#     while p and heap[p] > heap[c]:
#         heap[p], heap[c] = heap[c], heap[p]
#         c = p   # 부모와 부모의 부모를 비교...
#         p = c // 2
#
# N = int(input())
# arr = list(map(int, input().split()))
#
# heap = [0] * (N + 1)    # N개의 정점을 가진 완전이진트리
# last = 0    # 마지막 정점 번호
# for x in arr:
#     enq(x)
#
# ans = 0
# c = last
# while c // 2 > 0:
#     c //= 2
#     ans += heap[c]
# print(ans)

# 완전 이진 트리 (swea 5176)
def f(t):
    global cnt
    if t <= N:
        f(t * 2)
        # print(t, end=' ')
        cnt += 1
        tree[t] = cnt
        f(t * 2 + 1)

N = int(input())

tree = [0] * (N + 1)    # 노드번호를 인덱스로 사용해서 저장
cnt = 0
f(1)    # 완전이진트리 루트부터 중위순회
print(tree)