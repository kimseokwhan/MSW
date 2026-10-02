import sys
sys.stdin = open("electric_bus2_input.txt")

def charge(cur, battery):
    global cnt
    N = Ni[0]

    charge()



T = int(input())
for tc in range(1, T+1):
    Ni = list(map(int, input().split()))

    cnt = 0

    # for i in range(2, N):
    #     battery -= 1
    #     if battery < Ni[i]:
    #         if Ni[i] < Ni[i+1] + 1 and battery != 0:
    #             continue
    #         battery = Ni[i]
    #         cnt += 1

    charge(1, Ni[1])   # 현재 위치, 배터리 잔량

    print(f'#{tc} {cnt}')