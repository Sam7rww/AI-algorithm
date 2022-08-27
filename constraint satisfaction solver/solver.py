import sys
from queue import Queue
import math


class Variable:
    def __init__(self, name, length, domain=None):
        if domain is None:
            domain = []
        self.name = name
        self.length = length
        self.domain = domain

    def find_domain(self, dic_list):
        self.domain = dic_list.setdefault(self.length, [])


class Constraint:
    def __init__(self, v1, pos1, v2, pos2):
        self.v1 = v1
        self.v2 = v2
        self.pos1 = pos1
        self.pos2 = pos2

    def satisfied(self, assignment):
        # For current constraint
        # if either one variable is not in assignment, this constraint won't work
        if self.v1 not in assignment or self.v2 not in assignment:
            return True

        return assignment[self.v1][self.pos1] == assignment[self.v2][self.pos2]


class CSP:
    def __init__(self, variables, domains, constraints):
        # variables : List[str]
        # domains : Dict[variable, List[str]]
        # constraints : Dict[variable, List[Constraint]]
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.recursive = 1
        for variable in self.variables:
            if variable not in domains:
                raise LookupError("Every variable should have its domain(including [])")

    def consistent(self, variable, assignment):
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True

    def select_unassigned_variable(self, assignment):
        unassigned = []
        for v in self.variables:
            if v not in assignment:
                # v is not in assignment, now calculate domain size and constrain size
                domain_size = 0
                constraint_size = len(self.constraints[v])
                for value in self.domains[v]:
                    assignment[v] = value
                    if self.consistent(v, assignment):
                        domain_size += 1
                assignment.pop(v, "")

                for constraint in self.constraints[v]:
                    if constraint.v1 == v and constraint.v2 in assignment:
                        constraint_size -= 1

                unassigned.append([v, domain_size, constraint_size])

        unassigned.sort(key=lambda x: [x[1], -x[2]])
        # print("temp unassigned is:")
        # print(unassigned)
        return unassigned[0][0]

    def backtrack(self, assignment):
        if len(assignment) == len(self.variables):
            return assignment
        '''
        # get all variables in the CSP but not in the assignment
        unassigned = [v for v in self.variables if v not in assignment]

        # get the every possible domain value of the first unassigned variable
        first = unassigned[0]
        '''
        first = self.select_unassigned_variable(assignment)
        for value in self.domains[first]:
            assignment[first] = value
            if self.consistent(first, assignment):
                self.recursive += 1
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(first)

        return None

    def backtracking_search(self):
        return self.backtrack({}), self.recursive


dictionary_list = {}
xword_row = 0
xword_col = 0
xword = []
# store the mapping for every position in table
table_list = {}

# variable mapping: str to class
variable_mapping = {}


def parse_xword(data_file):
    global xword_row, xword_col, xword
    xword_file = open(data_file)
    row = 0
    for line in xword_file.readlines():
        str_list = line.split()
        if len(str_list) == 2:
            xword_row = int(str_list[0])
            xword_col = int(str_list[1])
            xword = [["X" for i in range(xword_col)] for j in range(xword_row)]
        else:
            for i in range(len(str_list)):
                xword[row][i] = str_list[i]
            row += 1


def parse_dictionary(data_file):
    global dictionary_list
    dict_file = open(data_file)
    dict_num = 0
    for line in dict_file.readlines():
        line = line.strip()
        dict_num += 1
        dictionary_list.setdefault(len(line), []).append(line)
    return dict_num


def find_variable_length(i, j, name, direct):
    global xword, table_list
    table_list.setdefault(str(i) + "," + str(j), []).append([name, 0])
    length = 1
    # direct 0: right ; 1: down
    if direct == 0:
        while j + 1 < xword_col and xword[i][j + 1] != "X":
            j = j + 1
            table_list.setdefault(str(i) + "," + str(j), []).append([name, length])
            length += 1
        return length
    else:
        while i + 1 < xword_row and xword[i + 1][j] != "X":
            i = i + 1
            table_list.setdefault(str(i) + "," + str(j), []).append([name, length])
            length += 1
        return length


def build_variable():
    global xword, table_list
    variable_list = []
    for i in range(xword_row):
        for j in range(xword_col):
            # row num: i, col num: j
            if xword[i][j] == "X":
                continue
            elif xword[i][j].isdigit():
                if j - 1 < 0 or xword[i][j - 1] == "X":
                    name = xword[i][j] + "-across"
                    variable_list.append(name)
                    length = find_variable_length(i, j, name, 0)
                    temp = Variable(name, length)
                    temp.find_domain(dictionary_list)
                    variable_mapping[name] = temp

                if i - 1 < 0 or xword[i - 1][j] == "X":
                    name = xword[i][j] + "-down"
                    variable_list.append(name)
                    length = find_variable_length(i, j, name, 1)
                    temp = Variable(name, length)
                    temp.find_domain(dictionary_list)
                    variable_mapping[name] = temp

    return variable_list


def revise(domains=None, constraint=Constraint("", "", "", "")):
    if domains is None:
        domains = {}
    revised = False
    v1 = constraint.v1
    v2 = constraint.v2
    for x_value in domains[v1]:
        satisfy_num = 0
        for y_value in domains[v2]:
            local_assign = {v1: x_value, v2: y_value}
            if constraint.satisfied(local_assign):
                satisfy_num += 1
                break
        if satisfy_num == 0:
            # delete x_value from domain
            # print("delete from " + v1 + " " + x_value)
            domains[v1].remove(x_value)
            revised = True
    return revised


def ac_3(variables=None, domains=None, constraints=None):
    if constraints is None:
        constraints = {}
    if domains is None:
        domains = {}
    if variables is None:
        variables = []
    q = Queue()
    for every_value in constraints.values():
        for temp_constraint in every_value:
            q.put(temp_constraint)

    while not q.empty():
        cur_constraint = q.get()
        cur_xi = cur_constraint.v1
        cur_xj = cur_constraint.v2
        if revise(domains, cur_constraint):
            if len(domains[cur_xi]) == 0:
                return False
            for every_neigh in constraints[cur_xi]:
                if every_neigh.v2 != cur_xj:
                    q.put(every_neigh)

    return True


# Run as: python astar_search.py FILENAME
def main():
    print("handle input data!")
    xwordfile = sys.argv[1]
    parse_xword(xwordfile)
    dictfile = sys.argv[2]
    dict_num = parse_dictionary(dictfile)
    # build the list of variable first
    variable_list = build_variable()

    print(str(dict_num) + " words")
    # build the Dict of all constraints
    constraint_list = {}
    constraint_num = 0
    for i in range(xword_row):
        for j in range(xword_col):
            key = str(i) + "," + str(j)
            value = table_list.get(key, [])
            if len(value) == 2:
                constraint_num += 1
                v1 = value[0][0]
                pos1 = value[0][1]
                v2 = value[1][0]
                pos2 = value[1][1]
                # temp_constraint = Constraint(v1, pos1, v2, pos2)
                constraint_list.setdefault(v1, []).append(Constraint(v1, pos1, v2, pos2))
                constraint_list.setdefault(v2, []).append(Constraint(v2, pos2, v1, pos1))

    print(str(constraint_num) + " constraints")
    print("")

    # build the domain of all variables
    domain_list = {}
    print("Initial assignment and domain sizes:")
    for value in variable_list:
        temp_domian = variable_mapping[value].domain
        domain_list[value] = temp_domian.copy()
        possible = len(temp_domian)
        print(value + " = NO_VALUE (" + str(possible) + " values possible)")

    print("")

    arc_check = None
    if (len(sys.argv)-1) == 3:
        arc_check = sys.argv[3]
    if arc_check is not None:
        print("Doing arc-consistency pre-processing...")
        print("")
        ac_3(variable_list, domain_list, constraint_list)
        print("Initial assignment and domain sizes:")
        for value in variable_list:
            new_length = len(domain_list[value])
            print(value + " = NO_VALUE (" + str(new_length) + " values possible)")

    print("")
    csp = CSP(variable_list, domain_list, constraint_list)
    solution, recursive_num = csp.backtracking_search()
    if solution is None:
        print("No solution found! after " + str(recursive_num) + " recursive calls to search.")
    else:
        print("SUCCESS! Solution found after " + str(recursive_num) + " recursive calls to search.")
        print("")
        print(solution)
        for i in range(xword_row):
            line = ""
            for j in range(xword_col):
                key = str(i) + "," + str(j)
                value = table_list.get(key, [])
                if len(value) == 0:
                    line += " "
                else:
                    v1 = value[0][0]
                    pos1 = value[0][1]
                    line += solution[v1][pos1]
            print(line)


main()
