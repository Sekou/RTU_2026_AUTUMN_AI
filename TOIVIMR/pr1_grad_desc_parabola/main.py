#TODO: сделать автоподбор скоростей для a b c на основе экспертных метрик сходимости

import sys, pygame
import numpy as np
import math
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    screen.blit(font.render(s, True, (0,0,0)), (x,y))
sz = (800, 600) 

pts=[
 [50, 500],
 [100, 400],
 [150, 320],
 [200, 280],
 [250, 260],
 [300, 300],
 [350, 360],
 [400, 420],
 [450, 490]
] 

# y=(x-200)^2 + 400

scale=1/600
a=1*scale
b=-200*scale
c=40000*scale + 400

def drawFunc(screen):
    p_last=None
    for x in np.arange(0,800,10):
        p=[x, a*x*x+b*x+c]
        if p_last is not None:
            pygame.draw.line(screen, (0,255,0), p_last, p, 2) 
        p_last=p

def calcMSE():
    global a, b, c
    res=0
    for p in pts:
        x=p[0]
        dy=p[1]-(a*x*x+b*x+c)
        res+=dy*dy
    return res/len(pts)

def gradDescent(eta):
    global a, b, c
    dEda, dEdb, dEdc = 0, 0, 0
    for p in pts:
        x=p[0]
        delta=(a*x*x+b*x+c)-p[1]
        dEda += delta*x*x
        dEdb += delta*x
        dEdc += delta
        # print(delta)
    a-=eta*dEda/len(pts)/10000
    b-=eta*dEdb/len(pts)/10
    c-=eta*dEdc/len(pts)/100

screen = pygame.display.set_mode(sz)
timer = pygame.time.Clock()
while True:
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            sys.exit(0)
    for i in range(10):
        gradDescent(0.000001) # выполнение шага градиентного спуска
    screen.fill((255, 255, 255))
    for p in pts:
        pygame.draw.circle(screen, (0,0,0), p, 5, 2)
    drawFunc(screen)
    mse=calcMSE()
    drawText(screen, f"MSE = {mse:.2f}", 5, 5)
    pygame.display.flip()
    timer.tick(20) 

#2026, S. Diane