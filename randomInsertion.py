import data as dataModule
import parameters
import utilities as utils
import solution as solutionModule
import copy

class RandomInsertion:
    data = None
    employees = list()  # internal variable to shuffle employees (list of int)
    unassigned_mandatory = list() # [week] = list of mandatory shifts that have to be covered
    unassigned_intermediate = list()  # [week] = list of intermediate shifts that have to be covered
    weekend_indexes = list() # internal variable to shuffle the weekends

    def __init__(self, data):
        self.data = data
        self.employees = range(len(data.employees))
        self.unassigned_shift = [list() for w in range(data.weeks)]
        self.weekend_indexes = range(data.weeks)

    def update_unassigned_shift(self, solution):
        """ Scans solution and update unassigned_shift. """
        self.unassigned_shift = [list() for w in range(self.data.weeks)]
        for day, day_timetable in range(self.data.days):
            for shift_id, employees in enumerate(day_timetable):
                if not employees:
                    self.unassigned_shift[day // 7].append(self.data.shifts[shift_id])

    def repair(self, solution):
        """ Repair solution. """
        