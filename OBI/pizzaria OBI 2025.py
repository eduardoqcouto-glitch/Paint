try:
    G = int(input(""))
    P = int(input(""))
except ValueError:
    print("Esse é um valor inválido")
    exit()

fatias_totais = G * 8 + P * 4

print(fatias_totais - 2)