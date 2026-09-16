import sys
sys.stdin = open("break_brick_input.txt")

T = int(input())
for tc in range(1, T+1):
    N, W, H = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(H)]
    min_v = 12 * 15
    block_num = 0