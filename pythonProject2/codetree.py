n = int(input())
commands = [tuple(input().split()) for _ in range(n)]
x = []
dir = []
for num, direction in commands:
    x.append(int(num))
    dir.append(direction)

# Please write your code here.
OFFSET = 100000
tile = [0] * (OFFSET * 2 + 1)
color_b = [0] * (OFFSET * 2 + 1)
color_w = [0] * (OFFSET * 2 + 1)
now = OFFSET

for i in range(n):
    if dir[i] == 'R':
        for j in range(now, now+x[i]):
            tile[j] = 1
            color_b[j] += 1
        now += x[i]
    else:
        for k in range(now - x[i], now):
            tile[k] = 2
            color_w[k] += 1
        now -= x[i]

cnt_b = 0
cnt_w = 0
cnt_g = 0

for l in range(len(tile)):
    if color_b[l] >= 2 and color_w[l] >= 2:
        cnt_g += 1
    elif tile[l] == 1:
        cnt_b += 1
    elif tile[l] == 2:
        cnt_w += 1

print(cnt_w, cnt_b, cnt_g)