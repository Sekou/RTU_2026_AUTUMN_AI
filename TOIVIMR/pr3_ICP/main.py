import math
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos
kpi=np.pi/180


def drawPoints(pts):
    glPointSize(3)
    glBegin(GL_POINTS)
    for p in pts:
        glVertex3fv(p)
    glEnd()
def drawAxes():
    for v in np.array(((1,0,0),(0,1,0),(0,0,1))):
        glColor(v)
        glBegin(GL_LINES)
        glVertex3fv((0,0,0))
        glVertex3fv(v)
        glEnd()

def rotate(pts, r, p, y):
    cr, cp, cy = cos(r), cos(p), cos(y)
    sr, sp, sy = sin(r), sin(p), sin(y)
    myaw = [[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]] # z
    mpit = [[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]] # y
    mrol = [[1, 0, 0], [0, cr, -sr], [0, sr, cr]] # x
    mat = np.array(myaw) @ mpit @ mrol
    res = mat.dot(np.transpose(pts))
    res = np.transpose(res)
    return res

def main():
    pygame.init()
    display=(800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0,0,-3)
    #разворот системы координат, чтоб ось Z была направлена вверх
    glMultMatrixf([ [0,0,-1,0],[-1,0,0,0],[0,1,0,0],[0,0,0,1] ])
    glTranslatef(0,0,-0.5)

    resultShift=None
    resultRotation=None

    pts=[
    [0.5,0.3,0.4],
    [0.2,0.3,0.4],
    [0.5,0.7,0.4],
    [0.5,0.3,0.6],
    [0.5,0.5,0.5]
    ]
    pts2 = rotate(pts, 45*kpi, 0, 0)
    pts2 = pts2 + [0.5,0.3,0.1]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key==K_1:
                    shift=findShift(pts, pts2)
                    pts2-=shift
                    if resultShift is None:
                        resultShift=-shift
                    resultRotation = np.eye(3)
                if event.key==K_2:
                    axis, ang=findRotation(pts, pts2)
                    pCenter=np.mean(pts2, axis=0)
                    pts2, R = rotateAroundAxis(pts2, pCenter, axis, -ang)
                    resultRotation=R @ resultRotation

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glClearColor(1, 1, 1, 1)
        glRotate(1, 0,0,1) #поворот на 1 градус вокруг оси Z
        drawAxes()
        glColor((1,0,0))
        drawPoints(pts)
        glColor((0,0,1))
        drawPoints(pts2)
        pygame.display.flip()
        pygame.time.wait(50)

def findShift(pts, pts2):
    p1=np.mean(pts, axis=0)
    p2=np.mean(pts2, axis=0)
    delta=p2-p1
    return delta

def findRotation(pts, pts2):
    p1 = np.mean(pts, axis=0)
    p2 = np.mean(pts2, axis=0)
    axis=np.zeros(3)
    ang=0
    for p in pts:
        dd=[np.linalg.norm(p-q) for q in pts2]
        i = np.argmin(dd)
        q=pts2[i]
        v1=p-p1
        v2=q-p2
        #ищем ось вращения
        u = np.cross(v1,v2)
        u/=np.linalg.norm(u)
        #ищем величину угла поворота
        cos_a=np.dot(v1, v2)/np.linalg.norm(v1)/np.linalg.norm(v2)
        a=math.acos(cos_a)
        axis+=u
        ang+=a
        axis/=len(pts)
        ang/=len(pts)
    return axis, ang

def rotateAroundAxis(pts, pCenter, axis, ang):
    ux,uy,uz=axis/np.linalg.norm(axis)
    c,s = cos(ang), sin(ang)
    c_=1-c
    pts2=np.subtract(pts, pCenter)
    R=np.array([[c+ux**2*c_, ux*uy*c_-uz*s, ux*uz*c_+uy*s],
    [uy*ux*c_+uz*s, c+uy**2*c_, uy*uz*c_-ux*s],
    [uz*ux*c_-uy*s, uz*uy*c_+ux*s, c+uz**2*c_]])
    res=R.dot(np.transpose(pts2))
    res=np.transpose(res)+pCenter
    return res, R



main()


