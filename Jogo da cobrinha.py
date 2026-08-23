import time
import msvcrt
import random
import os
import json

os.system("")
tabuleiro = [
    ['#','#','#','#','#','#','#','#','#','#','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#','O',' ',' ',' ',' ',' ','🍎',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#',' ',' ',' ',' ',' ',' ',' ',' ',' ','#'],
    ['#','#','#','#','#','#','#','#','#','#','#'],
]
def Tabuleiro():
    for l in tabuleiro:
        for c in l:
            if c == '🍎':
                print(c, end=' ')
                continue
            print(c, end="  ")
        print()
Tabuleiro()
player = [(5, 1)]
def morreu(pos):
    l, c = pos
    if tabuleiro[l][c] == '#':
        return True
    elif tabuleiro[l][c] == 'o':
        return True
    return False
def Tabuleirocheio():
    for l in tabuleiro:
        for c in l:
            if c == ' ':
                return False
    return True
def nova_maca():
    vazio = []
    if Tabuleirocheio():
        return "Não tem como colocar mais maçãs"
    else:
        for l in range(1,10):
            for c in range(1,10):
                if tabuleiro[l][c] == ' ':
                    vazio.append((l,c))
        l, c = random.choice(vazio)
        tabuleiro[l][c] = '🍎'
def mover(direcao, score):
    
    l, c = player[0]
    if direcao == 'd':
        mov = (l, c + 1)
    elif direcao == 'a':
        mov = (l, c - 1)
    elif direcao == 'w':
        mov = (l - 1, c)
    elif direcao == 's':
        mov = (l + 1, c)

    nl, nc = mov
    if tabuleiro[nl][nc] == '#':
        print("Você morreu!")
        return None, score
    if mov in player:
        return None, score
    if tabuleiro[nl][nc] == '🍎':
        score += 1
        nova_maca()
        player.insert(0, mov)
    else:
        player.insert(0, mov)
        player.pop()
    return True, score

def loadhighest_score():
    with open("Jogos maneiros/highscore.json", 'r',) as arq:
        dados = json.load(arq)
        return dados.get('highscore', 0)
def highestscore(score):
    with open('Jogos maneiros/highscore.json', 'w',) as arq:
        json.dump({'highscore': score},arq, indent=4)
def atualizar_tabuleiro():
    for l in range(len(tabuleiro)):
        for c in range(len(tabuleiro[0])):
            if tabuleiro[l][c] in ['O', 'o']:
                tabuleiro[l][c] = ' '

    for i, (l, c) in enumerate(player):
        if i == 0:
            tabuleiro[l][c] = 'O'   
        else:
            tabuleiro[l][c] = 'o'    

score = 0
direcao = 'd'
opostos = {
    'w':'s',
    's':'w',
    'a':'d',
    'd':'a'
}
os.system('cls')
highscore = loadhighest_score()
time.sleep(3)
while True:

    if msvcrt.kbhit():
        tecla = msvcrt.getwch().lower()
        if tecla in ['w','a','s','d'] and tecla != opostos[direcao]:
            direcao = tecla

    vivo, score = mover(direcao, score)

    if not vivo:
        os.system('cls')
        atualizar_tabuleiro()
        Tabuleiro()
        if score > highscore:
            highestscore(score)
            highscore = score
            print(f"Você bateu o recorde! {highscore}")

        print("Você morreu!")
        break
    print("\033[H", end="")
    atualizar_tabuleiro()
    print(f"Score: {score} | Highest score: {highscore}")
    Tabuleiro()

    time.sleep(0.18)

while True:
    if msvcrt.kbhit():
        n = msvcrt.getwch()
        if n == 'q':
            break