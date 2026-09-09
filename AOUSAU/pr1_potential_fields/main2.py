import pygame

"""
движение по методу потенциальных полей 
(реактивная стратегия уклогнения от препятствий + диссиапативный эффект затухания скорости)
"""


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

SPEED=10
DELTA=10

def dist(p1, p2): return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
def get_vec(p1, p2): return ((p2[0]-p1[0]),(p2[1]-p1[1]))
def get_norm_vec(p1, p2): 
    v,d=get_vec(p1, p2), dist(p1, p2)
    return (v[0]/d, v[1]/d)

class Particle:
    def __init__(self, x, y, r, m, q): 
        self.radius,self.m,self.q = r,m,q
        self.x,self.y=x,y
        self.vx,self.vy=0,0
        self.ax,self.ay=0,0
        self.fx,self.fy=0,0
        self.traj=[]
        self.stop=False
    def get_pos(self): return (self.x,self.y)
    def draw(self, screen):
        c=(0, 255, 0) if self.q>=0 else (255, 0, 0)
        pygame.draw.circle(screen, c, (self.x,self.y), self.radius)
        if len(self.traj)>1: pygame.draw.lines(screen, (130,130,130), False, self.traj, 1)
    def sim(self, dt):
        if self.stop: self.vx, self.vy=0,0
        else:
            self.ax, self.ay=self.fx/self.m, self.fy/self.m #2й-закон ньютона F=ma 
            self.vx, self.vy=self.vx+self.ax*dt, self.vy+self.ay*dt #численное интегрирование 1
            self.vx, self.vy=self.vx*0.99, self.vy*0.99
        self.x, self.y=self.x+self.vx*dt, self.y+self.vy*dt #численное интегрирование 2
        if len(self.traj)==0 or dist(self.traj[-1], self.get_pos())>DELTA:
            self.traj.append(self.get_pos())

fps=60
dt=1/fps

particles=[Particle(100, 50, 20, 1, 1), #робот
           Particle(350, 250, 100, 100000, 1), #препятствие 
           Particle(700, 500, 10, 100000, -10)] #цель

def calc_forces(particles):
    for i,a in enumerate(particles):
        a.fx, a.fy=0,0
        for j,b in enumerate(particles):
            if j==i: continue
            d=dist(a.get_pos(), b.get_pos())
            d=max(DELTA,d) #DELTA - предельное расстоянние сближения
            vec=get_norm_vec(a.get_pos(), b.get_pos())
            F=-1000000 * a.q*b.q / d**2
            if i==0: 
                print(j, F)
            a.fx, a.fy=a.fx+vec[0]*F, a.fy+vec[1]*F

running = True
while running:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for iter in range(SPEED):

        calc_forces(particles)

        for p in particles: p.sim(dt)

        if dist(particles[0].get_pos(), particles[-1].get_pos())<2*DELTA: 
            particles[0].stop=True

    # 3. Clear Screen (prevents the circle from leaving a "trail")
    screen.fill((255, 255, 255))  # Fills screen with black

    for p in particles: p.draw(screen)

    # 5. Flip/Update the display
    pygame.display.flip()
    clock.tick(fps)  # Limits game to 60 FPS

pygame.quit()