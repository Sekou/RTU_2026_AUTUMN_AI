import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, (0,0,0)), (x,y))
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    ang=ang%(2*arc); return ang + (2*arc if ang<-arc else -2*arc if ang>arc else 0)
def dist(p1,p2): return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
def get_segm_intersection(A, B, C, D): # поиск точки пересечения двух отрезков
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = A, B, C, D
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0: return None  # отрезки параллельны или совпадают
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1: return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None
def rot(v, ang): return np.dot([[-v[1], v[0]], v],[math.sin(ang), math.cos(ang)]) # поворот вектора на угол
def rot_arr(vv, ang): return [rot(v, ang) for v in vv] # функция для поворота массива на угол
   

OBJ_SZ=20
LIDAR_LEN=200
class Robot:
    def __init__(self, id, x, y):
        self.id=id
        self.radius, self.color=20, (0,0,0)
        self.x, self.y, self.alpha, self.vlin, self.vrot=x,y,0, 0,0
        self.dada=np.arange(-1, 1.001, 0.1)
        self.rays=[Ray(self.x, self.y, self.alpha+da, LIDAR_LEN) for da in self.dada]
        self.highlighted=False
    def get_pos(self): return [self.x, self.y]
    def get_sensor_vec(self): return [ round(dist(self.get_pos(), r.get_measured_pt())/LIDAR_LEN, 2) for r in self.rays]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        if self.highlighted:
            pygame.draw.circle(screen, (0,255,0), p1, self.radius, 0)
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.alpha), math.cos(self.alpha)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
        for r in self.rays: r.draw(screen)
        draw_text(screen,f"{self.id}", *self.get_pos())
    def sim(self, dt, objs):
        s,c=math.sin(self.alpha), math.cos(self.alpha)
        self.x, self.y=self.x+c*self.vlin*dt, self.y+s*self.vlin*dt
        self.alpha=lim_ang(self.alpha+self.vrot*dt)
        for r,da in zip(self.rays, self.dada): 
            r.set_pos(self.get_pos())
            r.alpha=self.alpha+da
        oo=[o for o in objs if dist(o.get_pos(), self.get_pos())<LIDAR_LEN+OBJ_SZ]        
        for r in self.rays:
            r.intresection_pt=None
            all_pts=[]
            for o in oo:
                ss=o.get_segments()
                pp=[get_segm_intersection(r.get_pos(), r.get_end_pos(), s[0], s[1]) for s in ss]
                all_pts.extend([p for p in pp if p is not None])
            if len(all_pts)>0:
                all_pts=sorted(all_pts, key=lambda p: dist(p, r.get_pos()))
                r.intresection_pt=all_pts[0]

class Obj: #небольшой объект на экране с отрезками
    def __init__(self, x, y): self.x, self.y, self.sz = x, y, OBJ_SZ
    def get_pos(self): return [self.x, self.y]
    def get_bb(self): return [self.x-self.sz/2, self.y-self.sz/2, self.sz, self.sz]
    def get_segments(self): 
        pp=[[self.x+dx*self.sz/2, self.y+dy*self.sz/2] for dx,dy in [[-1,-1], [-1,1], [1,1], [1,-1]]]
        return [ [a,b] for a,b in zip(pp, pp[1:]+[pp[0]] ) ]
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen): pygame.draw.rect(screen, (0, 0, 0), self.get_bb(), 2)

class Bar: #балка
    def __init__(self, x, y, ang, w, l): self.x, self.y, self.ang, self.w, self.l = x, y, ang, w, l
    def get_pos(self): return [self.x, self.y]
    def get_pts(self): 
        pp=[[dx*self.l/2, dy*self.w/2] for dx,dy in [[-1,-1], [-1,1], [1,1], [1,-1]]]
        pp = rot_arr(pp, self.ang)
        return [[x+self.x, y+self.y] for x,y in pp]
    def get_segments(self): 
        pp=self.get_pts()
        return [ [a,b] for a,b in zip(pp, pp[1:]+[pp[0]] ) ]
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen): 
        pp=self.get_pts()
        pygame.draw.lines(screen, (0, 0, 0), True, pp, 2)

class Ray: #луч дальномера
    def __init__(self, x, y, alpha, L): 
        self.x, self.y, self.alpha, self.L = x, y, alpha, L
        self.intresection_pt=None
    def get_pos(self): return [self.x, self.y]
    def get_end_pos(self): return [self.x+self.L*math.cos(self.alpha), self.y+self.L*math.sin(self.alpha)]
    def set_pos(self, p): self.x, self.y = p
    def get_measured_pt(self): return self.intresection_pt if self.intresection_pt is not None else self.get_end_pos()
    def draw(self, screen): 
        pygame.draw.line(screen, (255, 0, 0), self.get_pos(), self.get_measured_pt(), 1)
        if self.intresection_pt is not None: pygame.draw.circle(screen, (0,0,255), self.intresection_pt, 3, 2)

if __name__=="__main__":
    sz, timer, fps = (800, 600), pygame.time.Clock(), 20
    screen, dt = pygame.display.set_mode(sz), 1 / fps

    robot = Robot(0, 200, 200)
    robot2 = Robot(1, 200, 300)
    bar = Bar(100, 100, 1, 30, 150)

    def align_bar(robot, robot2):
        bar.x, bar.y = np.mean([robot.get_pos(), robot2.get_pos()], axis=0)
        dp=np.subtract(robot2.get_pos(), robot.get_pos())
        bar.ang=math.atan2(*dp[::-1])
    def align_robots(robot, robot2, bar):
        L=bar.l
        vec = rot([1,0], bar.ang)

        p1=np.add(bar.get_pos(), -vec*L/2)
        p2=np.add(bar.get_pos(), vec*L/2)

        robot.x=p1[0]
        robot.y=p1[1]
        robot2.x=p2[0]
        robot2.y=p2[1]

        a=bar.ang-math.pi/2
        a1=lim_ang(robot.alpha-a)
        a2=lim_ang(robot2.alpha-a)
        print(a1, a2)
        if a1>0.3: robot.alpha -= (a1-0.3)
        if a1<-0.3: robot.alpha += (-0.3-a1)
        if a2>0.3: robot2.alpha -= (a2-0.3)
        if a2<-0.3: robot2.alpha += (-0.3-a2)
        return a1, a2

    np.random.seed(0)
    objs = [ Obj(np.random.randint(50,750), np.random.randint(50,550) ) for i in range(20)]

    DT_SAMPLE=0.5
    last_time=0
    sim_time=0

    samples=[]

    MODE="MANUAL"

    a1,a2=0,0

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                robot.vlin = 50 if ev.key == pygame.K_w else -50 if ev.key == pygame.K_s else robot.vlin
                robot.vrot = -1 if ev.key == pygame.K_a else 1 if ev.key == pygame.K_d else robot.vrot
                if ev.key == pygame.K_1:
                    with open("samples.txt", "w") as f:
                        f.write(str(samples))
                    print(f"Saved {len(samples)} samples")
                    samples.clear()
                if ev.key == pygame.K_2:
                    MODE="NEURAL" if MODE=="MANUAL" else "MANUAL"

                robot2.vlin, robot2.vrot=robot.vlin, robot.vrot
                # a1=lim_ang(math.atan2(*np.subtract(bar.get_pos(), robot.get_pos())[::-1])-robot.alpha)
                # a2=lim_ang(math.atan2(*np.subtract(bar.get_pos(), robot2.get_pos())[::-1])-robot2.alpha)
                
                robot.highlighted=False
                robot2.highlighted=False
                if robot.vrot>0 and abs(a1)>0.2: 
                    robot2.vlin=robot.vlin/10
                    # robot2.vrot=robot.vrot/2
                    robot.highlighted=True
                if robot.vrot<0 and abs(a2)>0.2: 
                    robot.vlin=robot2.vlin/10
                    # robot.vrot=robot2.vrot/2
                    robot2.highlighted=True
                if ev.key == pygame.K_SPACE:
                    robot.highlighted=False
                    robot2.highlighted=False
                    a=bar.ang-math.pi/2 #глобальный угол поперечного направления балки
                    robot.alpha=robot2.alpha=a
                    robot.vrot=robot2.vrot=0
                    robot.vlin=robot2.vlin=0

        sens_vec=[float(v) for v in robot.get_sensor_vec()]

        align_bar(robot, robot2)
        a1,a2 = align_robots(robot, robot2, bar)

        robot.sim(dt, objs)
        robot2.sim(dt, objs)
        control_vec=[float(np.sign(robot.vlin)), float(np.sign(robot.vrot))]

        if MODE=="MANUAL":
            if sim_time-last_time>DT_SAMPLE:
                samples.append([control_vec, sens_vec])
                last_time=sim_time

        screen.fill((255, 255, 255))

        robot.draw(screen)
        robot2.draw(screen)
        bar.draw(screen)

        for obj in objs: obj.draw(screen)

        draw_text(screen, f"Sensors = {sens_vec}", 5, 5)
        draw_text(screen, f"Control = {control_vec}", 5, 25)
        draw_text(screen, f"Num samples = {len(samples)}", 5, 45)
        draw_text(screen, f"MODE = {MODE}", 5, 65)
        pygame.display.flip(), timer.tick(fps)
        sim_time+=dt

#template file by S. Diane, RTU MIREA, 2024-2025