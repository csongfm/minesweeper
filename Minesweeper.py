from tkinter import *
from tkinter import messagebox
import random

class MinesweeperCell(Label):
    def __init__(self, master, bomb, value, coord, color):
        '''Initializes a single minesweeper cell
        bomb = boolean, whether or not the cell has a bomb
        value = number of adjacent bombs
        color is color of text
        coord is location of cell'''
        
        Label.__init__(self, master, height=1 , width=2, text='',  \
                       relief = 'raised', bg='white', font=('Arial', 18), fg = color)
        self.bomb = bomb
        self.value = 0  #Set to 0 at beginning, changed during creation
        self.coord = coord  
        self.revealed = False
        self.color = color
        
        #Bind handlers to left and right clicks
        self.bind("<Button-1>", self.left_click)
        self.bind("<Button-2>", self.right_click)
        
        

    def is_bomb(self):
        '''MinesweeperCell.is_bomb()
        returns a boolean, whether the cell has a bomb or not'''
        return self.bomb

    def get_value(self):
        '''MinesweeperCell.get_value()
        returns the number in the cell'''
        return self.value

    def get_coord(self):
        '''MinesweeperCell.get_coord()
        returns the coordinates of a minesweeper cell on a grid'''
        return self.coord
    
    def is_revealed(self):
        '''MinesweeperCell.is_revealed()
        returns whether the cell is already revealed or not'''
        return self.revealed

    def left_click(self, event = None):
        '''MinesweeperCell.left_click()
        handler method for a left click on a cell'''
        
        if self.revealed:  #If they click on an already revealed cell, nothing
            pass
        else:
            self.revealed = True   #Reveal the cell
            if self.is_bomb():   #If it's a bomb
                for bomb in self.master.bombsList:
                    bomb['fg'] = 'black'
                    bomb['text'] = "*"
                    bomb['bg'] = 'red'
                    bomb['relief'] = 'sunken'
                for cell in self.master.cellDict.values():  #Show all remaining bombs
                    if cell['text'] == '*' and cell.is_bomb() == False:
                        cell['text'] = 'X'
                        cell['fg'] = 'red'

                messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)  #Display losing message
                        
            else:   #Not a bomb
                if self.get_value() != 0:
                    self['text'] = str(self.value)  # display the number
                self['relief'] = 'sunken'
                self['bg'] = 'gray'
                
                if self.get_value() == 0 and self.is_bomb() == False:  #If cell has no neighboring bombs, reveal all neighbors
                    neighborList = self.get_neighbors()
                    for neighbor in neighborList:   #Keep looping until all cells that are empty/adjacent to an empty cell are revealed
                        if neighbor['relief'] == 'raised':
                            neighbor.left_click()
                else:
                    pass
                    #no need to do anything else now
         
        if self.master.numBombs - self.master.numFlags == 0 and self.master.all_revealed():  #Check for win
            messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)

    def right_click(self, event = None):
        '''MinesweeperCell.right_click()
        handler method for a right click on a minesweeper cell'''
        
        if self['text'] == '*':   #If there's a flag, remove it
            self['text'] = ''
            self['fg'] = self.color
            self.master.numFlags -= 1
            self.master.scoreVariable.set(self.master.numBombs - self.master.numFlags)  #Update score
            
        else:  #Place flag
            self['fg'] = 'black'
            self['text'] = '*'
            self.master.numFlags += 1
            self.master.scoreVariable.set(self.master.numBombs - self.master.numFlags)

        if self.master.numBombs - self.master.numFlags == 0 and self.master.all_revealed():  #Check for win
            messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)
                

    def get_neighbors(self):
        '''MinesweeperCell.get_neighbors()
        Used on a minesweeper cell to get a list of it's neighboring cells'''
        
        neighbors = []

        for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    if self.coord[0]+x >= 0 and self.coord[0]+x <= self.master.width - 1 and self.coord[1]+y >= 0 and self.coord[1]+y <= self.master.height - 1:
                        neighbors.append(self.master.cellDict[(self.coord[0] + x, self.coord[1] + y)])

        neighbors.remove(self)
        return neighbors


class MinesweeperGrid(Frame):
    
    def __init__(self, master, width, height, bombs):
        '''MinesweeperGrid.__init__(width, height, bombs)
        initializes a minesweeper game grid with bombs bombs'''
        
        Frame.__init__(self, master)  #Init parent cell
        self.grid()
        
        self.width = width   #Set attributes
        self.height = height
        self.numBombs = bombs

        self.numFlags = 0  #Initialize number of flags

        self.colorMap = ['gray','blue','darkgreen','red','purple','maroon','cyan','black','dim gray']  #Colors for text

        self.cellDict = {}

        for x in range(self.width):  #Create individual cells
            for y in range(self.height):
                self.cellDict[(x, y)] = MinesweeperCell(self, False, 0, (x,y), 'gray')
                self.cellDict[(x, y)].grid(row = y, column = x)
                

        self.bombsList = random.sample(list(self.cellDict.values()), self.numBombs)  #List of bombs
        for bomb in self.bombsList:  #Set attributes if it's a bomb
            bomb.bomb = True
            bomb.value = '*'
            bomb.color = 'black'

        for cell in self.cellDict.values():
            if cell.get_value() != '*':
                cellNeighbors = cell.get_neighbors()
                for neighbor in cellNeighbors:
                    if neighbor.is_bomb():
                        cell.value  = int(cell.value) + 1  #Set value of each cell (number of adjacent bombs)
                cell.color = self.colorMap[int(cell.value)]
                cell['fg'] = cell.color  #Set color based off of value

        self.scoreFrame = Frame(self, bg='black')  # new frame to hold score number at bottom
        self.scoreVariable = IntVar()
        self.scoreVariable.set(self.numBombs)
        self.scoreLabel = Label(self.scoreFrame, textvar = str(self.scoreVariable), font=('Arial', 20), bg = 'white').grid()
        self.scoreFrame.grid(row = self.height, column = 0, columnspan = self.width)

    def all_revealed(self):
        '''MinesweeperGrid.all_revealed()
        Checks if all cells in the grid are revealed/flagged
        Returns boolean'''
        
        allRevealed = True  #Initialize allRevealed
        for cell in self.cellDict.values():
            if cell.is_revealed() == False and cell.is_bomb() == False:  #If any cell is not revealed and it's not a bomb, not all revealed
                allRevealed = False

        return allRevealed
    
#Set up game to play       
root = Tk()
root.title('Minesweeper')

difficulty = ""
while difficulty not in ["eh", "h", "m", "e"]:
    difficulty = input("What difficulty would you like? eh = extra hard, h = hard, m = medium, e = easy")
       
if difficulty == "eh":
    ms = MinesweeperGrid(root, 40, 40, 320)
elif difficulty == "h":
    ms = MinesweeperGrid(root, 30, 16, 99)
elif difficulty == "m":
    ms = MinesweeperGrid(root, 16, 16, 40)
else:
    ms = MinesweeperGrid(root, 9, 9, 10)
    
root.mainloop()
