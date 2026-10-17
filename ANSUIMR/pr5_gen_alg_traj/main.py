import sys, pygame, numpy as np

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))

sz = (800, 600)

def rn(A): return A*(np.random.random()*2-1)
def dist(p1,p2): return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
def get_segm_intersection(A, B, C, D): # поиск точки пересечения двух отрезков
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = A, B, C, D
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0: return None  # отрезки параллельны или совпадают
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1: return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None

class Obj: #небольшой объект на экране с отрезками
    def __init__(self, x, y): self.x, self.y, self.sz = x, y, 100
    def get_pos(self): return [self.x, self.y]
    def get_bb(self): return [self.x-self.sz/2, self.y-self.sz/2, self.sz, self.sz]
    def get_segments(self): 
        pp=[[self.x+dx*self.sz/2, self.y+dy*self.sz/2] for dx,dy in [[-1,-1], [-1,1], [1,1], [1,-1]]]
        return [ [a,b] for a,b in zip(pp, pp[1:]+[pp[0]] ) ]
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen): pygame.draw.rect(screen, (0, 0, 0), self.get_bb(), 2)
    def intersects(self, pa, pb): 
        return any([get_segm_intersection(pa,pb, pc,pd) is not None
                    for pc, pd in self.get_segments()])

class Traj:
    def __init__(self):
        self.pts=[]
    def init_rand(self, n=10, eps=50):
        self.pts=[
            [np.random.randint(eps,sz[0]-eps), 
            np.random.randint(eps,sz[1]-eps)]]
        for i in range(n-1):
            x_prev, y_prev=self.pts[-1]
            self.pts.append([x_prev+rn(eps), y_prev+rn(eps)])
    def constrain(self, p_start, p_end):
        self.pts[0], self.pts[-1] = p_start, p_end
    def draw(self, screen, color=(0,0,255)):
        pygame.draw.lines(screen, color, False, self.pts, 2)

#TODO: 
def crossover(traj1, traj2): pass #например брать первую половину от 1 а второую - от 2
def mutate(traj): pass
def repopulate(trajs): pass

def Q(traj, objs):
    segms=zip(traj.pts[1:], traj.pts[:-1])
    L=sum([dist(p1,p2) for p1,p2 in segms])
    C=sum([sum([o.intersects(p1,p2) for p1,p2 in segms]) for o in objs])
    return 1000/(L+1000*C)

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    best_traj=None
    q_best=0

    traj=Traj()
    objs=[Obj(300, 250), Obj(500, 350)]
    p_start, p_end = [100,300], [700,300]
    L0=dist(p_start, p_end)
    n, eps=10, 2*L0/10
    traj.init_rand(n, eps)
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: print("Hi")                

        traj=Traj()
        traj.init_rand(n, eps)
        traj.constrain(p_start, p_end)
        q=Q(traj,objs)
        if q>q_best: q_best, best_traj=q, traj

        screen.fill((255, 255, 255))  
        traj.draw(screen)   
        best_traj.draw(screen, (0,255,0))   
        for obj in objs: obj.draw(screen)   
        
        draw_text(screen, f"Q = {q}", 5, 5)
        draw_text(screen, f"Q_best = {q_best}", 5, 25)
        pygame.display.flip(), timer.tick(fps)
        
#template file by S. Diane, RTU MIREA, 2024-2026