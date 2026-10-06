import sys
sys.stdin = open("divide_grorp_in.txt")

def findgroup(member):
    global ans
    if boss[member] == member:
        ans += 1
        return member
    ret = findboss(boss[member])
    return ret

def findboss(member):
    if boss[member] == member:
        return member
    ret = findboss(boss[member])
    return ret

def union(a, b):
    fa = findboss(a)
    fb = findboss(b)
    if fa == fb:
        return
    boss[fb] = fa

T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())
    arr = list(map(int, input().split()))

    boss = [i for i in range(N+1)]
    ans = 0
    for i in range(0, M*2, 2):
        union(arr[i], arr[i+1])

    for j in range(len(boss)):
        findgroup(j)

    # print(boss)
    print(f'#{tc} {ans-1}')     # boss 배열에서 0 빼야해서 -1