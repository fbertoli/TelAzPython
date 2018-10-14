#!/usr/bin/env python
# coding=utf-8

import shifts as shiftsModule
import employee as employeeModule
import parameters
import data as dataModule
from datetime import date, timedelta
import solver as solverModule


def main():
    # -- choose which test to run
    parameters_test = False
    data_test = False
    shift_test = False
    shift_select_test = False
    shift_adjacent_test = False
    employee__test = False
    solver_test = False

    # parameters_test = True
    # data_test = True
    # shift_test = True
    # shift_select_test = True
    # shift_adjacent_test = True
    # employee__test = True
    solver_test = True

    # -- testing parameters.py
    parameters.read_config()
    if parameters_test:
        print "TEST parameters"
        print "parameters.start date = ", str(parameters.start_date)
        print "parameters.end date = ", str(parameters.end_date)
        print "parameters.min rest hours = ", parameters.min_rest_hours
        print "parameters.file turni = ", parameters.file_turni
        print "parameters.file festività = ", parameters.file_festivita
        print "--------------------------------------------------\n"
        return

    # -- testing class Data
    data = dataModule.Data()
    if data_test:
        print "TEST Data"
        print "data.start_date = ", data.start_date
        print "data.end_date = ", data.end_date
        print "data.days = ", data.days
        print "data.weeks = ", data.weeks
        print "holidays"
        for i in range(data.days):
            if data.holidays[i]:
                print "  -", i, timedelta(i) + data.start_date
        print "--------------------------------------------------\n"
        return

    # -- testing class Shifts
    shifts = data.shifts
    if shift_test:
        print "TEST Shifts variables "
        print "shifts.mandatory = ", shifts.mandatory
        print "shifts.intermediate = ", shifts.intermediate
        print "shift.info = "
        for k in shifts.info.keys():
            print "  -", k
            for k2 in shifts.info[k].keys():
                print "    -", k2, " = ", shifts.info[k][k2]
        print "shifts.adjacency_matrix"
        for k in shifts.adjacency_matrix.keys():
            print "{0:<30} = {1}".format(str(k), shifts.adjacency_matrix[k])
        print "--------------------------------------------------\n"
        return

    # -- testing class Shifts
    shifts = data.shifts
    if shift_select_test:
        print "TEST Shift.select()"
        print "all shifts"
        print "\n".join(map(str, shifts))
        keys = [("notte", '*', 1, '*'), ('*', False, '*', 0), ('*','*', 6, '*'), ('*', '*', 4, '*')]
        for k in keys:
            print "\nkey = ",k
            print "  - ".join(map(str, [item for item in shifts.select(name=k[0], mandatory=k[1], day=k[2], week=k[3])]))
        print "--------------------------------------------------\n"

    # -- testing adjacent Shifts
    if shift_adjacent_test:
        print "TEST Shift.get_adjacent()"
        for s in shifts:
            print "\nshift = ", s
            print "  - ".join(map(str, [item for item in shifts.get_adjacent(s)]))
        print "--------------------------------------------------\n"

    if employee__test:
        print "TEST Employees"
        for employee in data.employees:
            print employee
            print
        print "--------------------------------------------------\n"
        return


    solver = solverModule.Solver(data)
    if solver_test:
        print "TEST Solver Creation"
        solver.solve()
        # solver.print_solution()
        print "--------------------------------------------------\n"
        return


if __name__ == "__main__":
    main()

