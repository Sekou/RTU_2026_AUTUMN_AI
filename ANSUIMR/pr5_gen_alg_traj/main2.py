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
    def __init__(self, pts=[]):
        self.pts=pts
        self.q=0
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

MIN_GENES=2
def crossover(traj1, traj2, objs): #например брать первую половину от 1 а второую - от 2
    i1_gene = np.random.randint(MIN_GENES, len(traj1.pts)-MIN_GENES+1)
    i2_gene = i1_gene #np.random.randint(MIN_GENES, len(traj2.pts)-MIN_GENES+1)
    q1=Q(traj1, objs)
    q2=Q(traj2, objs)
    pts1=traj1.pts[:i1_gene]+traj2.pts[i2_gene:]
    pts2=traj2.pts[:i2_gene]+traj1.pts[i1_gene:]
    traj3, traj4 = Traj(pts1), Traj(pts2)
    q3=Q(traj3, objs)
    q4=Q(traj4, objs)
    #print(f"q1={q1}, q2={q2}, q3={q3}, q4={q4}")
    #if max(q3, q4)>max(q1, q2):
        #print("BETTER ! ! !")
    return traj3, traj4

def mutate(traj): 
    edge=1
    if np.random.random()>0.5:
        i1_gene = np.random.randint(edge, len(traj.pts)-1 - edge)
        i2_gene = np.random.randint(i1_gene, len(traj.pts) - edge)
        traj.pts[i1_gene], traj.pts[i2_gene]=traj.pts[i2_gene], traj.pts[i1_gene]
    else:
        i_gene = np.random.randint(edge, len(traj.pts)-1 - edge)
        traj.pts[i_gene] = [traj.pts[i_gene][0] + rn(20), traj.pts[i_gene][1] + rn(20)]


def mutate_all(prob, num_elite=3):
    for i, tr in enumerate(trajs):
        if i>=num_elite and np.random.random()>prob:
            mutate(tr)

def evaluate_and_sort(trajs, objs): 
    for tr in trajs: tr.q=Q(tr, objs)
    #print("TRAJS")
    #print([tr.q for tr in trajs])
    trajs=sorted(trajs, key=lambda tr: tr.q, reverse=True)
    #print([tr.q for tr in trajs])
    return trajs

def repopulate(trajs, objs, N, num_elite=3):
    old_trajs=[*trajs]
    new_trajs=trajs[:len(trajs)//2] #удаление старых траекторий
    while len(new_trajs)<N: #восполнение
        i1_creature = np.random.randint(num_elite)
        i2_creature = np.random.randint(num_elite)#len(old_trajs)//2)
        tr1, tr2=crossover(old_trajs[i1_creature], old_trajs[i2_creature], objs)
        new_trajs = (new_trajs+[tr1, tr2])[:N]
    return new_trajs

def constrain_all(trajs, p_start, p_end):
    for traj in trajs: traj.constrain(p_start, p_end)   

def gen_alg_step(iter_ind, p_start, p_end, trajs, objs, N, prob):
    if iter_ind==0: trajs=evaluate_and_sort(trajs, objs)
    trajs=repopulate(trajs, objs, N)
    mutate_all(prob)
    constrain_all(trajs, p_start, p_end)
    trajs=evaluate_and_sort(trajs, objs)
    return trajs

def check_collision(traj, objs):
    segms=list(zip(traj.pts[1:], traj.pts[:-1]))
    C=sum([sum([o.intersects(p1,p2) for p1,p2 in segms]) for o in objs])
    return C>0

def Q(traj, objs):
    segms=list(zip(traj.pts[1:], traj.pts[:-1]))
    L=sum([dist(p1,p2) for p1,p2 in segms])
    C=sum([sum([o.intersects(p1,p2) for p1,p2 in segms]) for o in objs])
    #print(len(objs), len(traj.pts), len(list(segms)), C)
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

    N=10
    #инициализируем начальную популяцию
    trajs=[Traj() for i in range(N)]
    for traj in trajs: traj.init_rand(n, eps)

    iter_ind=0
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: print("Hi")                

        for step in range(1):
            trajs=gen_alg_step(iter_ind, p_start, p_end, trajs, objs, N, 0.05)

        q_best, best_traj=trajs[0].q, trajs[0] 

        screen.fill((255, 255, 255))  
        for traj in trajs: 
            c=(0,0,255)
            if check_collision(traj, objs): c=(255,255,0)
            traj.draw(screen, c)
        best_traj.draw(screen, (0,255,0))   
        for obj in objs: obj.draw(screen)   
        
        draw_text(screen, f"Iter = {iter_ind}", 5, 5)
        draw_text(screen, f"Q_best = {q_best}", 5, 25)
        pygame.display.flip(), timer.tick(fps)
        
#template file by S. Diane, RTU MIREA, 2024-2026