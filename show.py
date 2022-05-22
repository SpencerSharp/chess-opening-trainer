from pathlib import Path

positions = Path.cwd() / "build" / "positions"
i = 0
total = 0
first_ten = []
for sub in positions.iterdir():
    i += 1
    total += sub.stat().st_size
    if i < 10:
        first_ten.append(sub)
    if i % 10000 == 0:
        print(i)
print(i)
print(total)

