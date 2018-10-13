import parameters
from ortools.constraint_solver import pywrapcp

class Solver:
    solver = None
    data = None

    # -- VARS
    x_var = dict()      # employee -> dict(): shift -> variable
    we_var = dict()    # employee -> dict(): int representing week -> variable

    # -- CONSTRS
    cover_shift = dict()    # shift -> constr
    shift_per_week = dict() # employee, int (week) -> constr
    adjacent_shifts = dict() # shift -> constr
    max_type_shifts = dict() # shift name, int (week) -> constr
    weekend_var_definition = dict() # employee, int(week) -> constr
    weekend_consecutive = dict() # employee, int(week) -> constr


    def __init__(self, data):
        self.data = data
        self.solver = pywrapcp.Solver("simple_example")
        self.create_vars()
        self.create_constraints()

    def create_vars(self):
        for employee in self.data.employees:
            self.x_var[employee] = dict()
            for shift in self.data.shifts:
                if not employee.unavailable[shift]:
                    self.x_var[employee][shift] = self.solver.IntVar(0, 1, "x-{0}-{1}".format(employee.name, shift.name))

            self.we_var[employee] = dict()
            for we in range(0,(self.data.days) / 7):
                self.we_var[employee][we] = self.solver.IntVar(0, 1, "w-{0}-{1}".format(employee.name, we))


    def create_constraints(self):
        # -- mandatory shifts must be taken
        for shift in self.data.shifts:
            if shift.mandatory:
                self.solver.Add(sum(self.x_var[e][shift] for e in self.data.employees if not e.unavailable[shift]) > 0)


    def solve(self):
        pass

    def populate_solution(self):
        pass

    def to_string(self):
        pass
