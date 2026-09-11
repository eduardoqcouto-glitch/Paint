A = int(input())
B = int(input())
C = int(input())
D = int(input())
if not C >= B >= A or not 100 <= C <= 500 or not 10 <= D <= 100:
    exit()

if A <= C - D <= B:
    print("S")
else:
    print("N")