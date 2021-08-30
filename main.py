import tkinter as tk
import tkinter.ttk as ttk
from threading import Thread
from time import sleep
from tkinter import messagebox

def build_gui(dim):
    app = tk.Tk()
    App(app, dim).pack(side="bottom")
    app.mainloop()


class Node:
    def __init__(self,nodeValue, nodeDepth, heaurisitcValue, parentValue = None):
        self.nodeValue = nodeValue
        self.parentValue = None
        self.nodeDepth = nodeDepth
        self.heaurisitcValue = heaurisitcValue

    def create_possible_moves(self, parentValue = None):
        horizontalAxis, verticalAxis = self.find(self.nodeValue,'_')
        allMoves = [[horizontalAxis,verticalAxis-1],[horizontalAxis,verticalAxis+1],[horizontalAxis-1,verticalAxis],[horizontalAxis+1,verticalAxis]]
        possibleMoves = []
        for element in allMoves:
            child = self.moveBlankSpot(self.nodeValue,horizontalAxis,verticalAxis,element[0],element[1])
            if child is not None:
                possibleMoveNode = Node(child,self.nodeDepth+1,0, parentValue)
                possibleMoves.append(possibleMoveNode)
        return possibleMoves
        
    def moveBlankSpot(self,puz,horizontalAxis1,verticalAxis1,horizontalAxis2,verticalAxis2):
        if horizontalAxis2 >= 0 and horizontalAxis2 < len(self.nodeValue) and verticalAxis2 >= 0 and verticalAxis2 < len(self.nodeValue):
            puzzleInstance = []
            puzzleInstance = self.duplicate(puz)
            temp = puzzleInstance[horizontalAxis2][verticalAxis2]
            puzzleInstance[horizontalAxis2][verticalAxis2] = puzzleInstance[horizontalAxis1][verticalAxis1]
            puzzleInstance[horizontalAxis1][verticalAxis1] = temp
            return puzzleInstance
        else:
            return None
            

    def duplicate(self,root):
        array = []
        for element in root:
            emptyArray = []
            for secondElement in element:
                emptyArray.append(secondElement)
            array.append(emptyArray)
        return array    
            
    def find(self,puzzle,x):
        for element in range(0,len(self.nodeValue)):
            for secondElement in range(0,len(self.nodeValue)):
                if puzzle[element][secondElement] == x:
                    return element,secondElement
    
    
class App(tk.Frame):    
    def __init__(self, parent, dim, **kw):
        super().__init__(parent, **kw)
        parent.minsize(dim[0], dim[1])
        parent.title("CSC 523 PROJECT")
        self.stop = False
        self.done = False
        self.speed = 0.8
        self.make_ui_components()
        self.show_ui()
        self.start_background_processes()
        self.n = 3
        self.open = []
        self.closed = []

    def start_background_processes(self):
        self.t1 = Thread(target=self.algo_update)
        self.t1.setDaemon(True)
        self.t1.start()

    def stop_animation(self):
        self.stop = True
        self.done = False
        self.reinitialise_puzzle()

    def reinitialise_puzzle(self):
        self.puzzle_start_data.reset()
        self.puzzle_destination_data.reset()

    def show_ui(self):
        self.puzzle_start_data = Puzzle(self, {"tile_color": "red", "text": "Start Configuration"})
        self.puzzle_destination_data = Puzzle(self, {"tile_color": "green", "text": "Destination Configuration"})
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(after=self.puzzle_start_data, fill=tk.X, expand=True)

        
    def f(self,start,goal):
        return self.h(start.nodeValue,goal)+start.nodeDepth

    def h(self, start, goal):
        temp = 0
        for i in range(0,self.n):
            for j in range(0,self.n):
                if start[i][j] != goal[i][j] and start[i][j] != '_':
                    temp += 1
        return temp


    def algo_update(self):
        while True:
            while not self.puzzle_start_data.is_set() or not self.puzzle_destination_data.is_set() or self.done:
                if self.stop is True: self.done = False
            self.stop = False
            self.process(3, self.puzzle_start_data.algo_value, self.puzzle_destination_data.algo_value)
            self.done = True
            
    def getInversionCount(self, arr):
        inversion_count = 0
        empty_value = '_'
        for i in range(0, 9):
            for j in range(i + 1, 9):
                if arr[j] != empty_value and arr[i] != empty_value and arr[i] > arr[j]:
                    inversion_count += 1
        return inversion_count
 
    def isSolvable(self, puzzle) :
        inv_count = self.getInversionCount([j for sub in puzzle for j in sub])
        return (inv_count % 2 == 0)
    
    def process(self, n, start, goal):
        open = []
        closed = []
        for n, i in enumerate(start):
            if i == -1:
                start[n] = '_'
            else:
                start[n] = str(start[n])
        for n, i in enumerate(goal):
            if i == -1:
                goal[n] = '_'
            else:
                goal[n] = str(goal[n])
        start = [start[0:3], start[3:6], start[6:]]
        if self.isSolvable(start) == False:
            messagebox.showinfo("Debug", "8 Puzzle is not solvable")
            return
        goal = [goal[0:3], goal[3:6], goal[6:]]
        start = Node(start,0,0)
        start.fval = self.f(start,goal)
        open.append(start)
        cur = open[0]
        while True:
            if(cur == None):
                messagebox.showinfo("Debug", "No possible moves !!")
                break
            puzzleList = []
            for i in cur.nodeValue:
                for j in i:
                    puzzleList.append(j)
            for n, i in enumerate(puzzleList):
                if i == '_':
                    puzzleList[n] = -1
            puzzleList = [ int(x) for x in puzzleList ]
            self.puzzle_start_data.set_state(puzzleList, self.speed)
            
            if(self.h(cur.nodeValue,goal) == 0):
                messagebox.showinfo("Debug", "solution is reached !!")
                break
            newOpen = []
            for i in cur.create_possible_moves(cur):
                i.fval = self.f(i,goal)
                i.parentValue = cur
                newOpen.append(i)
            closed.append(cur)
            del open[0]
            newOpen.sort(key = lambda x:x.fval,reverse=False)
            for i in newOpen:
                open.append(i)
            closedList = []
            for i in closed:
                closedList.append(i.nodeValue)
            currentHasAnOpenNode = False
            for i in newOpen:
                if i.nodeValue not in closedList:
                    cur = i
                    currentHasAnOpenNode = True
                    break
            if(currentHasAnOpenNode == False):
                cur = cur.parentValue
            open.sort(key = lambda x:x.fval,reverse=False)


    def make_ui_components(self):
        self.label = tk.Label(self, text="8 PUZZLE PROBLEM with A* Algorithm", font=('Verdana', 15, 'bold'))
        self.label.pack(side=tk.TOP)
        self.increase_speed = tk.Button(self, text="+ speed", bg="blue", fg="blue", command=self.inc_speed)
        self.increase_speed.pack(side=tk.RIGHT, anchor=tk.N)
        self.decrease_speed = tk.Button(self, text="- speed", bg="blue", fg="blue", command=self.dec_speed)
        self.decrease_speed.pack(side=tk.RIGHT, anchor=tk.N)
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(after=self.label, fill=tk.X)

    def inc_speed(self):
        self.speed /= 2

    def dec_speed(self):
        self.speed *= 2


class Puzzle(tk.Frame):
    def __init__(self, parent, config, **kw):
        super().__init__(parent, **kw)
        self.b = [[], [], []]
        self.config = config
        self.init_algo()
        self.draw_puzzle()
        tk.Label(parent, text=config["text"], font=('Verdana', 10, 'bold'), pady=5).pack()
        self.val = tk.Label(parent, text="", font=('Verdana', 10, 'bold'), pady=2)
        self.val.pack()
        self.pack(pady=15)

    def init_algo(self):
        self.algo_value = [-1] * 9
        self.index = 1

    def draw_puzzle(self):
        for i in range(3):
            for j in range(3):
                self.b[i].append(self.button())
                self.b[i][j].config(command=lambda row=i, col=j: self.fill(row, col))
                self.b[i][j].grid(row=i, column=j)

    def set_state(self, move: list, speed: float):
        for n, i in enumerate(self.algo_value):
                if i == '_':
                    self.algo_value[n] = -1
        curr_row, curr_col = self.get_corr(self.algo_value.index(-1))
        new_row, new_col = self.get_corr(move.index(-1))
        b1, b2 = self.b[curr_row][curr_col], self.b[new_row][new_col]
        prop1, prop2 = self.get_prop(b1), self.get_prop(b2)
        self.set_prop(prop2, b1)
        self.set_prop(prop1, b2)
        self.algo_value = move[:]
        self.update()
        sleep(speed)

    def get_prop(self, b):
        return b.cget("text"), b.cget("bg")

    def set_prop(self, prop, b):
        b.config(text=prop[0], bg=prop[1])

    def mark_tile(self):
        index = self.algo_value.index(-1)
        row, col = self.get_corr(index)
        self.b[row][col].config(bg=self.config["tile_color"], state=tk.DISABLED)

    def button(self):
        return tk.Button(self, bd=5, width=2, font=('arial', 30, 'bold'))

    def fill(self, i, j):
        self.b[i][j].config(text=self.index, state=tk.DISABLED, bg="black", fg="white")
        self.algo_value[i * 3 + j] = self.index
        self.index += 1
        if self.index == 9:
            self.mark_tile()
            self.val.config(text=str(self.algo_value))
    def get_corr(self, index):
        return index // 3, index % 3

    def is_set(self):
        return self.index == 9

    def reset(self):
        self.init_algo()
        self.val.config(text="")
        for i in range(3):
            for j in range(3):
                self.b[i][j].config(text="", bg=self.cget('bg'), fg="black", state=tk.NORMAL)

build_gui(dim=(500, 500))
