import sys
import PIL
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable , words in self.domains.items():
            to_remove =set()
            for w in words:
                if len(w) != variable.length:
                    to_remove.add(w)
            self.domains[variable] = words.difference(to_remove)


    def revise(self, x, y):
        """
        USE PSEUDOCODE FROM THE LECTURE NODES
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False 
        overlap = self.crossword.overlaps[x, y]

        if overlap:
            v1, v2 = overlap
            to_remove = set()
            for xlap in self.domains[x]:
                overlapped = False
                for ylap in self.domains[y]:
                    if xlap != ylap and xlap[v1] == ylap[v2]:
                        overlapped = True
                        break
                if not overlapped:
                    to_remove.add(xlap)
            if to_remove:
                self.domains[x] = self.domains[x].difference(to_remove)
                revised = True 

        return revised

    def ac3(self, arcs=None):
        """
        USE PSEUDOCODE FROM THE LECTURE NOTES
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            Q=[ ]
            for var1 in self.domains:
                for var2 in self.crossword.neighbors(var1):
                    if self.crossword.overlaps[var1, var2] is not None:
                        Q.append((var1, var2))

        while Q:
            x,y = Q.pop(0)
            if self.revise(x,y):
                if len(self.domains[x]) ==0:
                    return False

                for n in self.crossword.neighbors(x):
                    if n != y:
                        Q.append((n, x))
            return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # traverse over all variables in the crossword
        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for varX, wordX in assignment.items():
            if varX.length != len(wordX):
                return False

            for varY, wordY in assignment.items():
                if varX != varY:
                    if wordX == wordY:
                        return False
                    overlap = self.crossword.overlaps[varX, varY]
                    if overlap:
                        a, b = overlap
                        if wordX[a] != wordY[b]:
                            return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        words={}

        for w in self.domains[var]:
            discard = 0
            for n in self.crossword.neighbors(var):
                if n in assignment:
                    continue
                else:
                    xoverlap, yoverlap = self.crossword.overlaps[var, n]
                    for i in self.domains[n]:
                        if w[xoverlap] != i[yoverlap]:
                            discard+=1
            words[w] = discard

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # initialize a list of potential variables to consider with heuristics (minimum remaining value and degree)
        potential = []
        for vari in self.crossword.variables:
            if vari not in assignment:
                potential.append([vari , len(self.domains[vari]),  len(self.crossword.neighbors(vari))])

        if potential:
            potential.sort(key=lambda x: (x[1], -x[2]))
            return potential[0][0]

        return None

    def backtrack(self, assignment):
        """
        USE PSEUDOCODE FROM THE LECTURE NOTES
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        # assignment is already complete (all variables have words), simply return assignment
        if self.assignment_complete(assignment): 
            return assignment
        variable = self.select_unassigned_variable(assignment)

        for value in self.domains[variable]:
            copy = assignment.copy()
            copy[variable] = value
            if self.consistent(copy):
                result =self.backtrack(copy)

                if result:
                    return result
               

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()