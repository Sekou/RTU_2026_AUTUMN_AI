#модель робота, перемещающегося в среде с препятствиями (потенциальными полями)
import sys, pygame, numpy as np, math, itertools

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, color=(0,0,0)): # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, (0,0,0)), (x,y))
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    ang=ang%(2*arc); return ang + (2*arc if ang<-arc else -2*arc if ang>arc else 0)
def dist(p1,p2): return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
def get_vec(p1, p2): return [(p2[0]-p1[0]),(p2[1]-p1[1])]
def get_unit_vec(p1, p2):
    d=dist(p1, p2)
    return [(p2[0]-p1[0])/d,(p2[1]-p1[1])/d]

class Robot:
    def __init__(self, x, y):
        self.radius, self.color=20, (0,0,0)
        self.x, self.y, self.a, self.vlin, self.vrot=x,y,0, 0,0
        self.q=1
        self.traj=[]
    def traj_len(self): return 0 if len(self.traj)<2 else sum([dist(*pp) for pp in zip(self.traj[:-1], self.traj[1:])])
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
        for p1,p2 in zip(self.traj[:-1], self.traj[1:]): pygame.draw.line(screen, (150,150,150), p1, p2,1)
    def sim(self, dt):
        s,c=math.sin(self.a), math.cos(self.a)
        self.x, self.y=self.x+c*self.vlin*dt, self.y+s*self.vlin*dt
        self.a=lim_ang(self.a+self.vrot*dt)
        if len(self.traj)==0 or dist(self.traj[-1], self.get_pos())>10: self.traj.append(self.get_pos())

class Obj:
    def __init__(self, x, y, r, q):
        self.x, self.y = x, y
        self.radius=r
        self.q=q
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        color=(255,0,0) if self.q>0 else (0,0,255)
        pygame.draw.circle(screen, color, self.get_pos(), self.radius, 2)

def calc_force(robot, objs, POWER):
    fx,fy=0,0
    for o in objs:
        d=dist(robot.get_pos(), o.get_pos())
        f=get_unit_vec(robot.get_pos(), o.get_pos())
        F=1000*o.q*robot.q/d**POWER
        fx,fy=fx+F*f[0],fy+F*f[1]
    return [fx,fy]

if __name__=="__main__":
    sz, timer, fps = (800, 600), pygame.time.Clock(), 20
    screen, dt = pygame.display.set_mode(sz), 1 / fps

    SIM_SPEED=30

    x0, y0=100,100
    robot, objs=None, None
    CHARGE_OBST, CHARGE_GOAL, POWER=0,0,0
    d0=0

    K1=[1, 2, 3]
    K2=[20,50,100]
    K3=[1,1.5,2,2.5]
    #формируем декартово произведение множеств для поиска оптимума на решетке значений
    K=list(itertools.product(K1, K2, K3))
    print("Num exp. =", len(K))
    print(K)

    def reset_world(id_experiment):
        global robot, objs, CHARGE_OBST, CHARGE_GOAL, POWER, d0
        robot = Robot(x0, y0)
        # несколько препятствий и цель
        CHARGE_OBST = K[id_experiment][0]
        CHARGE_GOAL = K[id_experiment][1]
        POWER=K[id_experiment][2]
        objs = [Obj(300, 150, 20, CHARGE_OBST),
                Obj(500, 450, 20, CHARGE_OBST),
                Obj(400, 300, 20, CHARGE_OBST),
                Obj(200, 300, 20, CHARGE_OBST),
                Obj(600, 250, 20, CHARGE_OBST),
                Obj(700, 500, 10, -CHARGE_GOAL)]
        d0 = dist([x0, y0], objs[-1].get_pos())

    exp_results=[]
    id_experiment=0
    reset_world(id_experiment)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                robot.vlin = 50 if ev.key == pygame.K_w else -50 if ev.key == pygame.K_s else robot.vlin
                robot.vrot = -1 if ev.key == pygame.K_a else 1 if ev.key == pygame.K_d else robot.vrot

        for iter in range(SIM_SPEED):

            LOST=dist(robot.get_pos(), objs[-1].get_pos())>d0*10

            if dist(robot.get_pos(), objs[-1].get_pos())>20 and not LOST:
                fvec=calc_force(robot, objs, POWER)
                da=lim_ang(robot.a-math.atan2(fvec[1], fvec[0]))
                robot.vrot=0.5*da
                robot.vlin=50
            else:
                robot.vrot=0
                robot.vlin=0
                if id_experiment < len(K):
                    print(K[id_experiment], robot.traj_len())
                    exp_results.append(robot.traj_len())
                    id_experiment+=1
                    if id_experiment < len(K):
                        reset_world(id_experiment)
                    else:
                        ind_best=np.argmin(exp_results)
                        print(f"D0 = {d0:.2f}")
                        print(f"RESULT: {ind_best}, D = {exp_results[ind_best]:.2f}, P = {K[ind_best]}")

            robot.sim(dt)

        screen.fill((255, 255, 255))
        robot.draw(screen)

        for o in objs: o.draw(screen)

        draw_text(screen, f"Id exp. = {id_experiment}", 5, 5)
        draw_text(screen, f"Traj. len = {robot.traj_len():.2f}", 5, 25)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2026
