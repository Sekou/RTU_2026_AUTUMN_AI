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

OBJ_SZ=20
LIDAR_LEN=200
class Robot:
    def __init__(self, x, y):
        self.radius, self.color=20, (0,0,0)
        self.x, self.y, self.alpha, self.vlin, self.vrot=x,y,0, 0,0
        self.dada=np.arange(-1, 1.001, 0.1)
        self.rays=[Ray(self.x, self.y, self.alpha+da, LIDAR_LEN) for da in self.dada]
    def get_pos(self): return [self.x, self.y]
    def get_sensor_vec(self): return [ round(dist(self.get_pos(), r.get_measured_pt())/LIDAR_LEN, 2) for r in self.rays]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.alpha), math.cos(self.alpha)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
        for r in self.rays: r.draw(screen)
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

class Obj: #небольшой объект на экране
    def __init__(self, x, y): self.x, self.y, self.sz = x, y, OBJ_SZ
    def get_pos(self): return [self.x, self.y]
    def get_bb(self): return [self.x-self.sz/2, self.y-self.sz/2, self.sz, self.sz]
    def get_segments(self): 
        pp=[[self.x+dx*self.sz/2, self.y+dy*self.sz/2] for dx,dy in [[-1,-1], [-1,1], [1,1], [1,-1]]]
        return [ [a,b] for a,b in zip(pp, pp[1:]+[pp[0]] ) ]
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen): pygame.draw.rect(screen, (0, 0, 0), self.get_bb(), 2)

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
    robot = Robot(200, 200)
    np.random.seed(0)
    objs = [ Obj(np.random.randint(50,750), np.random.randint(50,550) ) for i in range(20)]

    DT_SAMPLE=0.5
    last_time=0
    sim_time=0

    samples=[]

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

        robot.sim(dt, objs)
        sens_vec=robot.get_sensor_vec()
        control_vec=[float(np.sign(robot.vlin)), float(np.sign(robot.vrot))]

        if sim_time-last_time>DT_SAMPLE:
            samples.append([control_vec, sens_vec])
            last_time=sim_time

        screen.fill((255, 255, 255))
        robot.draw(screen)
        for obj in objs: obj.draw(screen)

        draw_text(screen, f"Sensors = {sens_vec}", 5, 5)
        draw_text(screen, f"Control = {control_vec}", 5, 25)
        draw_text(screen, f"Num samples = {len(samples)}", 5, 45)
        pygame.display.flip(), timer.tick(fps)
        sim_time+=dt

#template file by S. Diane, RTU MIREA, 2024-2025