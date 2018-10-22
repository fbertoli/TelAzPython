import parameters
from ortools.constraint_solver import pywrapcp
import sys

class Solver:
    solver = None
    decision_builder = None
    data = None

    # -- VARS
    x_var = dict()      # employee -> dict(): shift -> variable
    we_var = dict()    # employee -> dict(): int representing week -> variable
    all_vars = list()

    # -- CONSTRS
    cover_shift = dict()    # shift -> constr
    shift_per_week = dict() # employee, int (week) -> constr
    adjacent_shifts = dict() # employee, shift -> constr
    shifts_max_week = dict() # employee, shift name, int (week) -> constr
    we_var_definition = dict() # employee, int(week) -> constr
    we_consecutive = dict() # employee, int(week) -> constr

    def __init__(self, data):
        self.data = data
        self.solver = pywrapcp.Solver("simple_example")
        self.create_x_vars()
        self.create_we_vars()
        self.create_cover_shift_constraints()
        self.create_shift_per_week_constraints()
        self.create_adjacent_shifts_constraints()
        self.create_shifts_max_week_constraints()
        self.create_we_var_definition_constraints()
        self.create_we_consecutive_constraints()

    def create_x_vars(self):
        for employee in self.data.employees:
            self.x_var[employee] = dict()
            for shift in self.data.shifts:
                if not employee.unavailable[shift]:
                    self.x_var[employee][shift] = self.solver.IntVar(0,1,"x-E{0}-S{1}-D{2}".format(employee.id, shift.name, shift.day))
                    self.all_vars.append(self.x_var[employee][shift])

    def create_we_vars(self):
        for employee in self.data.employees:
            self.we_var[employee] = dict()
            for we in range(self.data.weeks):
                self.we_var[employee][we] = self.solver.IntVar(0,1,"w-{0}-{1}".format(employee.name, we))
                self.all_vars.append(self.we_var[employee][we])

    def create_cover_shift_constraints(self):
        # -- mandatory shifts must be taken
        for shift in self.data.shifts:
            if shift.mandatory:
                self.solver.Add(sum(self.x_var[e][shift] for e in self.data.employees if not e.unavailable[shift]) > 0)

    def create_shift_per_week_constraints(self):
        # -- employee must take correct number of shifts per week
        for e in self.data.employees:
            for w in range(self.data.weeks):
                self.solver.Add(sum(self.x_var[e][s] for s in self.data.shifts.select(name='*', mandatory='*', day='*', week=w) if not e.unavailable[s]) == e.shifts_per_week[w])

    def create_adjacent_shifts_constraints(self):
        # -- for each set of adjacent shifts, select at most 1, for each employee
        # counter = 0
        # for shift in self.data.shifts:
        #     adjacents = self.data.shifts.get_adjacent(shift)
        #     print "shift", shift
        #     print "adjacents", [(s.name, s.day) for s in adjacents]
        #     for e in self.data.employees:
        #         if not e.unavailable[shift]:
        #             print e.name, [(s.name, s.day) for s in adjacents if not e.unavailable[s]]
        #             self.solver.Add(sum(self.x_var[e][s] for s in adjacents if not e.unavailable[s]) <= 1)
        for d in range(self.data.days):
            if not self.data.holidays[d]:
                shifts = self.data.shifts.select(name='*', mandatory='*', day=d,week='*')
                for e in self.data.employees:
                    shifts_e = [s for s in shifts if not e.unavailable[s]]
                    if shifts_e and e.id in [0]:
                        self.solver.Add(sum(self.x_var[e][s] for s in shifts_e) < 2)
                        print d, e.name, ", ".join(map(lambda x: getattr(x, 'name'), shifts_e))

    def create_shifts_max_week_constraints(self):
        # -- for each shift type, employee can take a maximum per week
        for shift_name, max_shifts in parameters.shifts_max_week.items():
            for e in self.data.employees:
                for w in range(self.data.weeks):
                    self.shifts_max_week[e, shift_name, w] = self.solver.Add(
                        sum(self.x_var[e][s] for s in self.data.shifts.select(name=shift_name, mandatory='*', day='*', week=w)) <= max_shifts)

    def create_we_var_definition_constraints(self):
        # -- get number of shifts in a weekend
        for w in range(self.data.weeks):
            we_shifts = self.data.shifts.select(name='*', mandatory='*', day= w*7 +5, week=w) + self.data.shifts.select(
                name='*', mandatory='*', day=w*7+ 6, week=w)
            for e in self.data.employees:
                self.we_var_definition[e,w] = self.solver.Add(sum(self.x_var[e][s] for s in we_shifts if not e.unavailable[s]) < len(we_shifts)*self.we_var[e][w])

    def create_we_consecutive_constraints(self):
        for w in range(self.data.weeks - parameters.max_we_consecutive):
            for e in self.data.employees:
                self.we_consecutive[e,w] = self.solver.Add(sum(self.we_var[e][w + i] for i in range(parameters.max_we_consecutive)) <= parameters.max_we_consecutive)

    def solve(self):
        self.decision_builder = self.solver.Phase(self.all_vars, self.solver.CHOOSE_RANDOM, self.solver.ASSIGN_MIN_VALUE)
        solutions_limit = self.solver.SolutionsLimit(1)
        time_limit = self.solver.TimeLimit(3 * 1000)
        collector = self.solver.AllSolutionCollector()
        collector.Add(self.all_vars)
        if self.solver.Solve(self.decision_builder, [solutions_limit, collector]):
            print "Some solutions found"
            # self.print_solution()
            sol = 0
            while self.solver.NextSolution():
                print "writing ..."
                with open("solutions/sol-%s.txt"%sol, 'w') as target:
                    for day in range(self.data.days):
                        target.write("DAY %s\n" %day)
                        shifts = self.data.shifts.select(name='*', mandatory='*', day=day, week='*')
                        for s in shifts:
                            for e in self.data.employees:
                                if not e.unavailable[s] and self.x_var[e][s].Value() > 0:
                                    target.write("{0}: {1}\n".format(s.name, e.name))
                sys.exit()
                sol += 1
        else:
            print "No solutions found"

    def print_solution(self):
        sol = 0
        while self.solver.NextSolution():
            print "Solution", sol
            sol += 1
            for day in range(self.data.days):
                print "DAY",day
                shifts = self.data.shifts.select(name='*',mandatory='*',day=day,week='*')
                for s in shifts:
                    for e in self.data.employees:
                        if not e.unavailable[s] and self.x_var[e][s].Value() > 0:
                            print "{0}: {1}".format(s, e.name)
            # sys.exit()


        print("\nNumber of solutions found:", sol)


    def populate_solution(self):
        pass

    def to_string(self):
        pass
