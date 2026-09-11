N, M = input().split(" ")

N = int(N)
M = int(M)

if N > 30 or N < 1 or M > 300000 or M < 1:
    exit()

KL = 0

for i in range(N):

    P, G, C = input().split(" ")

    P = int(P)
    G = int(G)
    C = int(C)

    if 0 <= P <= 500 and 0 <= G <= 500 and 0 <= C <= 500:
        KL += P*4
        KL += G*9
        KL += C*4

    else:
        exit()

if M >= KL:
    print(M - KL)
else:
    print("Limite excedido")
