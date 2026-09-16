import pygame  
import sys  

#ДОП. ЗАДАНИЕ:
#1) сделать 2 препятствия состоящих из 10 частиц каждое
#2) протестировать значения степени 1.5 и 3 в формуле потенциалдльного поля
#3) подсчитать длину траекториии пройденной роботом
#4) визуализировать вектора потенциального поля 
# в точках 30*i, 30*j где i,j = 1,...,20


#частица
class Particle:
    def __init__(self, x, y, r, q, m):
        self.r,self.q,self.m = r, q, m #радиус, заряд, масса
        self.x,self.y = x, y #координаты
        self.vx,self.vy = 0, 0 #скорость
        self.ax,self.ay = 0, 0 #ускорение
        self.fx,self.fy = 0, 0 #сила
        self.traj=[]
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        color = (0,255,0) if self.q>=0 else (255,0,0) 
        pygame.draw.circle(screen, color, (self.x, self.y), self.r, 0)
        if len(self.traj)>2: 
            pygame.draw.lines(screen, (130,130,130), False, self.traj, 1)
    def sim(self, dt):
        #self.traj.append(self.get_pos())
        if len(self.traj)==0 or dist(self.traj[-1], self.get_pos())>10:
            self.traj.append(self.get_pos())
        self.ax,self.ay = self.fx/self.m,self.fy/self.m #F = ma, a = F/m
        self.vx,self.vy = self.vx+self.ax*dt,self.vy+self.ay*dt
        self.vx,self.vy= self.vx*0.999,self.vy*0.999
        self.x,self.y = self.x+self.vx*dt,self.y+self.vy*dt


def dist(p1,p2):
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
def get_vec(p1,p2):
    return [p2[0]-p1[0], p2[1]-p1[1]]
def get_unit_vec(p1,p2):
    v,d = [p2[0]-p1[0], p2[1]-p1[1]],dist(p1, p2)
    return [v[0]/d, v[1]/d]

def calc_force(particle, objs):
    fx,fy=0,0
    for o in objs:
        if o == particle: continue
        v=get_unit_vec(particle.get_pos(), o.get_pos())
        d=dist(particle.get_pos(), o.get_pos())
        d=max(10, d)
        F = -10000 * particle.q * o.q / d**2
        fx, fy=fx+v[0]*F,fy+v[1]*F
    particle.fx, particle.fy=fx, fy

# Инициализация Pygame  
pygame.init()  
  
# Установка размеров экрана  
screen_width, screen_height = 800, 600  
screen = pygame.display.set_mode((screen_width, screen_height))  
pygame.display.set_caption("Moving Point")  
  
# Главная переменная для цикла  
running = True  

particle=Particle(100,120, 20, 1, 1)
particle.fx=1
particle.fy=1
particle2=Particle(400,300, 30, 1, 100)
particle3=Particle(700,500, 20, -10, 100)

all_particles=[particle, particle2, particle3]

while running:  
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            pygame.quit()  
            sys.exit()  
  
    calc_force(all_particles[0], all_particles)
    for p in all_particles:
        p.sim(0.01)

    # Отрисовка точки  
    screen.fill((255,255, 255))  
    for p in all_particles:
        p.draw(screen)
    pygame.display.flip()
