import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))
def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2)) #расстояние между точками
def rot(v, ang): return np.dot([[-v[1], v[0]], v],[math.sin(ang), math.cos(ang)]) # поворот вектора на угол
def rot_arr(vv, ang): return [rot(v, ang) for v in vv] # функция для поворота массива на угол
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    return ang%(2*arc)+2*arc*(int(ang%(2*arc)<-arc)-int(ang%(2*arc)>arc))
def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина, высота и угол поворота прямогуольника
    pts = [[- w/2, - h/2],[+ w/2, - h/2],[+ w/2, + h/2],[- w/2, + h/2]]
    pygame.draw.polygon(screen, color, np.add(rot_arr(pts, ang), pc), 2)

sz = (800, 600)


class Cell: #ячейка
    def __init__(self, id, ix, iy, x, y):
        self.id=id
        self.ix=ix
        self.iy=iy        
        self.x=x
        self.y=y
        self.text = ""
        self.V=0
        self.selected = False
    def get_pos(self):
        return [self.x, self.y]

class Table: #таблица
    def __init__(self, x0, y0, width, height, nx, ny):
        self.x0,self.y0 =  x0, y0
        self.width,self.height = width, height
        self.nx,self.ny = nx, ny
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 25)
        num_сells=nx*ny
        w, h = self.width / self.nx, self.height / self.ny
        self.cells=[Cell(i, i%nx, i//nx, self.x0+w/2+(i%nx)*w, 
                         self.y0+h/2+(i//nx)*h) 
                         for i in range(num_сells)]
    def get_ix_iy(self, mouseX, mouseY):
        w, h = self.width / self.nx, self.height / self.ny
        iy = (mouseY - self.y0) / h
        ix = (mouseX - self.x0) / w
        return int(ix), int(iy)
    def get_cell(self, ix, iy): #объект ячейки
        #UPD 2
        if ix<0 or ix>=self.nx or iy<0 or iy>=self.ny: 
            return None
        return self.cells[iy*self.nx+ix]
    def get_cell_bb(self, ix, iy): #рамка ячейки
        y = round(self.y0 + iy * self.height / self.ny)
        y_ = round(self.y0 + (iy + 1) * self.height / self.ny)
        x = round(self.x0 + ix * self.width / self.nx)
        x_ = round(self.x0 + (ix + 1) * self.width / self.nx)
        return [x, y, x_ - x, y_ - y]
    def get_cell_center(self, ix, iy): #центр ячейки
        bb=self.get_cell_bb(ix, iy)
        return [bb[0]+0.5*bb[2], bb[1]+0.5*bb[3]]
    def draw(self, screen):
        for iy in range(self.ny):
            for ix in range(self.nx):
                #контур ячейки
                bb = self.get_cell_bb(ix, iy)
                c=self.cells[iy*self.nx+ix]
                color=(255, 0, 0) if c.selected else (50, 0, 0)
                w=3 if c.selected else 1
                pygame.draw.rect(screen, color, bb, w)
                # текст ячейки
                p = self.get_cell_center(ix,iy)
                #UPD 1
                draw_text(screen, c.text, p[0]-10, p[1]-10, sz=20)
                draw_text(screen, f"{c.V:.2f}", p[0]-20, p[1] + 10, sz=20, c=(255,0,0))

def get_neighbourhood(tb, x,y):
    for dy in [-1,0,1]:
        for dx in [-1,0,1]:
            if dy==0 and dx==0: continue
            c2=tb.get_cell(x+dx, y+dy)
            if c2 is not None: yield c2

def find_route(tb, x0, y0):
    c_curr=tb.get_cell(x0,y0)
    route=[c_curr]
    c_next=c_curr
    while True:
        found_next=False
        nb=list(get_neighbourhood(tb, c_curr.ix, c_curr.iy))
        for c2 in nb:
            if c2.V>c_next.V: 
                c_next=c2
                found_next=True
        if not found_next:
            return route
        c_curr=c_next
        route.append(c_next)

def value_iteration(tb, alpha, gamma):
    for i in range(tb.ny):
        for j in range(tb.nx):
            c=tb.get_cell(j, i)
            R=100 if c.text=="G" else -100 if c.text=="O" else 0
            
            V_nb=0
            if R==0: #warning проверить корректность такого жесткого условия
                V_nb=-100500
                for c2 in get_neighbourhood(tb, j, i):
                    V_nb=max(V_nb, c2.V)

                c.V_new=c.V+alpha*(R + gamma*V_nb - c.V)
            else:
                c.V_new=R
        
    for c in tb.cells: c.V=c.V_new #синхронизация


if __name__=="__main__":
    screen, timer, fps =  pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    width = 400  # ширина таблицы
    height = 300  # высота таблицы
    nx = 7  # число столбцов
    ny = 5  # число строк

    tb=Table(100,100, width,height, nx,ny)
    tb.cells[1*nx+2].text="O"
    tb.cells[1*nx+3].text="O"
    tb.cells[2*nx+3].text="O"
    tb.cells[2*nx+2].text="O"
    tb.cells[3*nx+3].text="O"

    tb.cells[0*nx+(nx-1)].text="G"

    route=[]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    value_iteration(tb, 0.3, 0.7)     
                if ev.key == pygame.K_2:
                    route=find_route(tb, 0, tb.ny-1)   
                    print("route",route)

        screen.fill((255, 255, 255))     

        tb.draw(screen)
        for a,b in zip(route[:-1], route[1:]):
            pygame.draw.line(screen, (0,0,255), a.get_pos(), b.get_pos(), 2)

        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2024-2026