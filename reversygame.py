from dataclasses import field
from random import randint
from sys import get_coroutine_origin_tracking_depth
from tkinter import Canvas, Tk, mainloop

W, H = 8, 8

CELLSIZE = 50
CELLCOLORS = ('khaki','coral4')
CHECKERCOLORS = ('red', 'white') 
BACKCOLOR = 'white'
BOTTOMGAP = 100

class ReversyLogic:
    def __init__(self, show_field, mode='twogamer') -> None:
        self.running = True
        self.show_field = show_field
        self.active = 0
        self.dirs = self.init_dirs()
        self.field = [[None] * W for i in range(H)]
        self.field[3][3] = self.field[4][4] = 0
        self.field[4][3] = self.field[3][4] = 1
        self.players = [0, 1]
        self.botnum = -1 if mode=='twogamer' else randint(0, 1)
        self.update()
    
    def init_dirs(self):
        dirs = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not i == j == 0:
                    dirs.append ((i, j))
        return dirs
    
    def bestturn(self):
        bestcells = [(0, 0), (W - 1, H - 1), (0, H - 1), (W - 1, 0)]
        best = None
        best_res = None
        for x in range (W):
            for y in range(H):
                if not self.possible(self.active, (x, y)):
                    continue
                if (x, y) in bestcells:
                    pass
                if (best is None) or \
                    (not best in bestcells) and ((x, y) in bestcells) or \
                        (len(self.occuped) > best_res):
                    best = (x, y)
                    best_res = len(self.occuped)
        return best


    def turn(self, coords):
        player = self.active
        if self.possible(player, coords):
            x, y = coords
            self.field[y][x] = player
            for cell in self.occuped:
                xc, yc = cell
                self.field[yc][xc] = player
            self.active = self.get_active()
            if self.active == self.botnum:
                self.turn(self.bestturn())
        self.update()
    
    def get_active(self):
        opp = self.opponent(self.active)
        if self.haspossibleturn(opp):
            return opp
        if not self.haspossibleturn(self.active):
            return None
        return self.active

    def haspossibleturn(self, player):
        for x in range(W):
            for y in range(H):
                if self.field[y][x] is None and self.possible(player, (x, y)):
                        return True
        return False 
    
    def possible(self, player, coords):
        x, y = coords
        return self.running and self.field[y][x] is None and self.isoccupedblank(player, coords)
    
    def isoccupedblank(self, player, coords):
        self.occuped = []
        x0, y0 = coords
        for dir in self.dirs:
            dx, dy = dir
            temp = []
            x = x0 + dx
            y = y0 + dy
            while 0 <= x < W and 0 <= y < H  and self.field[y][x] == self.opponent(player):
                temp.append((x, y))
                x += dx
                y += dy
            if 0 <= y < H and 0 <= x < W and self.field[y][x] == player:
                self.occuped += temp
        return len(self.occuped) > 0
    
    def winner(self):
        nums = [0, 0]
        for row in self.field:
            for i in row:
                if i is None:
                    continue
                nums[i] += 1
        for p in range(2):
            if nums[p] == 0:
               return self.opponent(p)
        if sum(nums) == W * H or self.active is None:
            return 'draw' if nums[0] == nums[1] else int(nums[0] < nums[1])      
        return None
    
    def update(self):
        winner = self.winner()
        msg = f"Player#{self.active}, select cell to turn" if winner is None \
        else f"{'There is draw' if winner == 'draw' else f'Player#{winner} win'}"
        self.show_field(self.field, msg)
        self.running = winner is None

    def neib(self, coords):
        x0, y0 = coords
        neib = []
        for x in range(max(0, x0 - 1), min(W, x0 + 2)):
            for y in range(max(0, y0 - 1), min(H, y0 + 2)):
                if not (x0 == x and y0 == y):
                    neib.append((x, y))
        return neib

    def opponent(self, player):
        return (player + 1) % 2



class Graphics:
    def __init__(self) -> None:        
        win = Tk()
        self.canvas = Canvas(win, width=CELLSIZE * W, height=CELLSIZE * H + BOTTOMGAP, bg = BACKCOLOR)
        self.info = self.canvas.create_text(CELLSIZE * W / 2, CELLSIZE * H + BOTTOMGAP / 2, \
            font = 'Tahoma 10', anchor='center', text='All right')
        self.canvas.pack()
        self.checkers = []
        self.drawboard()
        self.canvas.bind_all("<Button-1>", self.get_turncoords)
        mode = 'comp'
        self.logic = ReversyLogic(self.draw_field, mode)
        self.logic.update()
    
    def drawboard(self):
        for y in range(H):
            self.checkers.append([])
            for x in range(W):
                color = CELLCOLORS[(x + y) % 2]
                x1, y1 = x * CELLSIZE, y * CELLSIZE
                x2, y2 = x1 + CELLSIZE, y1 + CELLSIZE
                d = CELLSIZE / 6
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='white', width=3)
                checker = self.canvas.create_oval(x1 + d, y1 + d, x2 - d, y2 - d, width=0, state='hidden')
                self.checkers[-1].append(checker)
        self.canvas.update()

    def get_turncoords(self, event):
        x = event.x // CELLSIZE 
        y = event.y // CELLSIZE
        self.logic.turn((x, y))
    
    def draw_field(self, field, msg):
        self.canvas.itemconfig(self.info, text = msg)
        y = 0
        for row in field:
            x = 0
            for i in row:
                if i != None:
                    self.canvas.itemconfig(self.checkers[y][x], state='normal', fill = CHECKERCOLORS[i], width = i)
                x += 1
            y += 1
        self.canvas.update()



class Terminal:
    def __init__(self) -> None:
        self.g = ReversyLogic(self.print_field)
        while self.g.running:
            self.g.turn(self.get_turn())

    def print_field(self, field, msg):
        print(end = '    ')
        for i in range(W):
            print(i, end=' ')
        print()
        r = 0
        for row in field:
            print(f'{r} |', end=' ')
            for i in row:
                print(i if not i is None else '-', end = ' ')
            print()
            r += 1       
        print(f"{msg}. Two digits like this: '1 2'") 

    def get_turn(self):
        return [int(i) for i in input().split()]

    
#g = Terminal()

g = Graphics()
mainloop()




