import matplotlib.pyplot as plt
import numpy as np

with open("results.txt", "r", encoding="utf-16") as hd:
    lines = hd.readlines()

if not lines:
    print("Failed to open file")
    exit()

times = []
for line in lines:
    times.append(float(line.strip("\n")))

frequency = []
x = []
for i in np.arange(0, 100, 0.1):
    x.append(i)
    total = 0
    for time in times:
        if time <= i:
            total += 1
    fraction = total / 100
    frequency.append(fraction)

fig, ax = plt.subplots()

ax.stairs(frequency, linewidth=2.5)
ax.grid()
ax.set_xlim(0, 1000)
ax.set_ylim(0, 1)
ax.set_xticks([100, 200, 300, 400, 500, 600, 700, 800, 900])
ax.set_xticklabels([10, 20, 30, 40, 50, 60, 70, 80, 90])
ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Probabilidade")

plt.show()