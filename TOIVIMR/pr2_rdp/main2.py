import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))
def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2)) #расстояние между точками
def pt_segm_dist(p, p1, p2): # расстояние от точки до прямой (заданной отрезком)
    k = (p2[1]-p1[1]) / (0.0000001 if p2[0]==p1[0] else (p2[0]-p1[0]))
    return np.abs(k * (p1[0]-p[0]) - p1[1] + p[1]) / (k * k + 1)**0.5 # числитель: p[1]-(k*p[0]+b)

sz = (800, 600)

def do_rdp_new(pts, i1, i2):
    if check_eps(pts, i1, i2, EPS):
        return -1
    dd=[pt_segm_dist(p, pts[i1], pts[i2]) for p in pts]
    ii=np.argsort(dd)[::-1]
    ii=[i for i in ii if i1<i<i2]
    if len(ii): return ii[0]
    return -1

def do_rdp_recursive(pts, i1, i2, res=[], level=0, side="START"):
    print("  " * level + f"{side}: RDP {i1} {i2}")
    i = do_rdp_new(pts, i1, i2)
    if i1<i<i2:
        res.append(i)
        do_rdp_recursive(pts, i1, i, res, level+1, "L")
        do_rdp_recursive(pts, i, i2, res, level+1, "R")
    return i

if __name__=="__main__":
    screen, timer, fps =  pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    EPS=20

    pts=[[100, 100], [170, 150], [210, 170], 
         [270, 300], [330, 340], [400, 430], 
         [450, 450], [500, 420], [580, 460], 
         [620, 460], [670, 470], [700, 490]]
    pts=pts[::-1]
    
    p1, p2, pc = pts[0], pts[-1], None
    i1, i2 = 0, len(pts)-1
    pts_subset=pts
    nodes=[p1, p2]

    def check_eps(pts, i1, i2, eps):
        for i in range(i1+1, i2):
            if pt_segm_dist(pts[i], pts[i1], pts[i2])>eps: return False
        return True

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    ii=[]
                    do_rdp_recursive(pts, i1, i2, ii)
                    ii_sorted=sorted([0]+ii+[len(pts)-1])
                    nodes=[pts[i] for i in ii_sorted]

        screen.fill((255, 255, 255))   
        for p in pts:
            pygame.draw.circle(screen, (0,0,0), p, 5, 2)  
        
        pygame.draw.circle(screen, (255,0,0), p1, 10, 1)  
        pygame.draw.circle(screen, (255,0,0), p2, 10, 1)  
        #pygame.draw.line(screen, (255,0,0), p1, p2, 1)

        if pc is not None:
            pygame.draw.circle(screen, (255,0,255), pc, 10, 1)
            pygame.draw.line(screen, (130,130,130), p1, pc, 1)
            pygame.draw.line(screen, (130,130,130), pc, p2, 1)

        pygame.draw.lines(screen, (0,255,0), False, nodes, 2)

        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2024-2026