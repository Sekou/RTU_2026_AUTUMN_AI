import sys, pygame, numpy as np, math
from fuz import *
import matplotlib.pyplot as plt
import itertools

#ДОП. задание - сделать, чтоб робот парковался задним ходом (вместо переднего)
#ДОП. задание - обучить робота объезжать препятствия
#TODO: формировать оценку достоверности как величину обратно пропорциональную скорости выхода на парковку D0/D


pygame.font.init()
def draw_text(screen, s, x, y):
    screen.blit(pygame.font.SysFont('Comic Sans MS', 20).render(s, True, (0,0,0)), (x,y))

sz = (800, 600)

def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def lim_ang(ang):
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rot_arr(vv, ang): return [rot(v, ang) for v in vv]# функция для поворота массива на угол

def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2))

def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [[- w/2, - h/2],[+ w/2, - h/2],[+ w/2, + h/2],[- w/2, + h/2]]
    pygame.draw.polygon(screen, color, np.add(rot_arr(pts, ang), pc), 2)

class ParkingArea:
    def __init__(self, x, y, sz):
        self.x, self.y = x, y
        self.sz=sz
    def get_parking_point(self):
        return [self.x+self.sz/2, self.y+self.sz]
    def get_random_point(self):
        return [self.x+self.sz*np.random.random(), self.y+self.sz*np.random.random()]
    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), [self.x,self.y,self.sz,self.sz], 2)
        pygame.draw.circle(screen, (255,0,0), p:=self.get_parking_point(), 5, 2)
        pygame.draw.line(screen, (255,0,0), p, [p[0], p[1]-self.sz], 1)

class Robot:
    def __init__(self, x, y, alpha):
        self.x, self.y = x, y
        self.alpha=alpha
        self.L, self.W = 70, 40
        self.vsteer = 0
        self.speed, self.steer = 0, 0
        self.traj=[] #точки траектории
    def get_pos(self): return [self.x, self.y]
    def clear(self):
        self.traj, self.vals1, self.vals2  = [], [], []
    def draw(self, screen):
        p=np.array(self.get_pos())
        draw_rot_rect(screen, (0,0,0), p, self.L, self.W, self.alpha)
        dx, dy=self.L/3, self.W/3
        dd=rot_arr([[-dx,-dy], [-dx,dy], [dx,-dy], [dx,dy]], self.alpha)
        for d, k in zip(dd, [0,0,1,1]):
            draw_rot_rect(screen, (0, 0, 0), p+d,
                        self.L/5, self.W/5, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            pygame.draw.line(screen, (0,0,255), self.traj[i], self.traj[i+1], 1)
    def sim(self, dt):
        self.added_traj_pt = False
        delta=rot([self.speed*dt, 0], self.alpha)
        self.x+=delta[0]
        self.y+=delta[1]
        self.steer=self.steer+self.vsteer*dt
        self.steer=min(max(-0.7, self.steer), 0.7)
        if self.steer!=0:
            R = self.L/self.steer
            da = self.speed*dt/R
            self.alpha=lim_ang(self.alpha+da)
        if len(self.traj)==0 or dist(self.get_pos(), self.traj[-1])>10:
            self.traj.append(self.get_pos())
            self.added_traj_pt=True
    def goto(self, pos, dt):
        v=np.subtract(pos, self.get_pos())
        aGoal=math.atan2(v[1], v[0])
        da=lim_ang(aGoal-self.alpha)
        self.steer += 0.5 * da * dt
        maxSteer=1
        if self.steer > maxSteer: self.steer = maxSteer
        if self.steer < -maxSteer: self.steer = -maxSteer
        self.speed = 50
    def get_traj_len(self):
        return sum([dist(a,b) for a, b in zip(self.traj[:-1], self.traj[1:])])

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20

    robot=Robot(100, 100, 1)
    pa=ParkingArea(50,50,500)

    time=0
    DT_UPD=0.5
    time_last_update= -DT_UPD-0.000001

    goal = [600,400]

    MODE="MANUAL" #"AUTO"

    table=[]
    tables=[]
    filtered_fuz_table=[]

    fv_x = FuzzyVar(-10, 10)
    fv_x.add_term("BN", -10, 10)
    fv_x.add_term("N", -5, 10)
    fv_x.add_term("Z", 0, 10)
    fv_x.add_term("P", 5, 10)
    fv_x.add_term("BP", 10, 10)
    #fv_x.draw(plt)
    #plt.show()

    wa=3.14
    fv_a = FuzzyVar(-wa, wa)
    fv_a.add_term("BN", -wa, wa)
    fv_a.add_term("N", -wa/2, wa)
    fv_a.add_term("Z", 0, wa)
    fv_a.add_term("P", wa/2, wa)
    fv_a.add_term("BP", wa, wa)
    #fv_a.draw(plt)
    #plt.show()

    ws=0.7*2
    fv_s = FuzzyVar(-ws, ws)
    fv_s.add_term("N", -ws/2, ws)
    fv_s.add_term("Z", 0, ws)
    fv_s.add_term("P", ws/2, ws)
    #fv_s.draw(plt)
    #plt.show()

    def get_term_name(x, fv):
        fv.calc(x)
        aa=[t.activation for t in fv.terms]
        t=fv.terms[np.argmax(aa)]
        return t.name

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_w: robot.speed=50
                if ev.key==pygame.K_s: robot.speed=-50
                if ev.key==pygame.K_a: robot.vsteer=-2
                if ev.key==pygame.K_d: robot.vsteer=2
                if ev.key==pygame.K_1: 
                    with open("tables_final.txt", "r") as f:
                        tables=eval(f.read())
                        table=list(itertools.chain(*tables))
                        fuz_table=[]
                        for x,a,s,gamma in table:
                            res=[get_term_name(x, fv_x), get_term_name(a, fv_a), get_term_name(s, fv_s), float(round(gamma, 4))]
                            fuz_table.append(res)
                        #отберем из нечеткой таблицы только самые достоверные записи
                        fuz_table.sort(key=lambda x: x[:3])
                        filtered_fuz_table=[] 
                        for key, group in itertools.groupby(fuz_table, key=lambda x: x[:2]):
                            for item in group: filtered_fuz_table.append(list(group)[0])
                        with open("fuz_table.txt", "w") as f2:
                            f2.write(str(filtered_fuz_table))
                if ev.key==pygame.K_2:
                    MODE="AUTO" if MODE=="MANUAL" else "MANUAL"

        dt=1/fps

        x=robot.x-pa.get_parking_point()[0]
        a=lim_ang(robot.alpha-math.pi/2)
        L=robot.get_traj_len()

        if abs(x)<10 and abs(a)<0.1:
            print("Parking succeeded")
            robot.x, robot.y = pa.get_random_point()
            if robot.y>pa.y+pa.sz/2: robot.y-=pa.sz/2
            robot.traj=[]
            tables.append([*table])
            with open("tables.txt", "w") as f:
                f.write(str(tables))
            table=[]

        if time-time_last_update>=DT_UPD:
            gamma=1/(1+0.01*L) #чем дольше траектория тем она менее достоверна
            gamma=float(round(gamma, 4))
            #TODO: возможно в конце надо все достоверности в табце помножать на достоверность последнего элемента
            table.append([x, a, robot.steer, gamma])
            time_last_update=time

        if MODE=="AUTO":
            def find_matching_rule(x, a, fv_x, fv_a, filtered_fuz_table):
                n1=get_term_name(x, fv_x)
                n2=get_term_name(a, fv_a)
                res=None
                for i, (X, A, S, G) in enumerate(filtered_fuz_table):
                    if X==n1 and A==n2: 
                        res=filtered_fuz_table[i]
                        break
                return res
            
            r=find_matching_rule(x, a, fv_x, fv_a, filtered_fuz_table)
            if r is not None:
                robot.steer=fv_s.defuzz_term_name(r[2])
                robot.speed=50

        #robot.goto(goal, dt)
        robot.sim(dt)

        screen.fill((255, 255, 255))
        robot.draw(screen)
        pa.draw(screen)
        pygame.draw.circle(screen, (255,0,0), goal, 5, 2)
        draw_text(screen, f"Time = {time:.3f}", 5, 5)
        draw_text(screen, f"X = {x:.1f}, A = {a:.3f}", 5, 25)
        draw_text(screen, f"L = {L:.1f}", 5, 45)
        draw_text(screen, f"M = {MODE}", 5, 65)
        pygame.display.flip(), timer.tick(fps)
        time+=dt

#template file by S. Diane, RTU MIREA, 2024-2026