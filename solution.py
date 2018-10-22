import data as dataModule
import parameters
import utilities as utils

class Solution:
    data = None
    timetable = list()   # [day][shift.id] : list of employees assigned on shift
    schedule = list()    # [employee.id][day] =  shift object  (note one shift per day is allowed)
    weekends = list()    # [employee.id][week] = number of shifts employee works on weekend
    available_shifts = list() # [employee.id][week] = number of shift employee still has to be assigned to

    def __init__(self, data):
        self.data = data
        self.timetable = [[[] for s in data.shifts] for d in range(data.days)]
        self.schedule = [[data.shifts.dummy for d in range(data.days)] for e in data.employees]
        self.weekends = [[0 for w in range(data.weeks)] for e in data.employees]
        self.available_shifts = [[e.shifts_per_week[w] for w in range(data.weeks)] for e in data.employees]

    # -- MODIFICATION METHODS
    def remove_shift(self, employee, day):
        """ Remove employee from shift on given day"""
        # -- check if employee has an assigned shift on given day
        shift = self.schedule[employee.id][day]
        if shift.id > -1:
            # -- remove from timetable and schedule
            self.timetable[day][shift.id].remove(employee)
            self.schedule[employee.id][day] = self.data.shifts.dummy

            # -- if shift was on the weekend adjust weekends
            week = day // 7
            if self.data.is_on_weekend(day):
                self.weekends[employee.id][week] -= 1
                utils.safety_check(self.weekends[employee.id][week] >= 0, "self.weekends[{0}][{1}] = {2}".format(employee.name,day // 7, self.weekends[employee.id][week]))

            # -- upate count
            self.available_shifts[employee.id][week] += 1

    def remove_all_shifts(self, employee):
        for day in range(self.data.days):
            shift = self.schedule[employee.id][day]
            if shift.id > -1:
                # -- remove from timetable and schedule
                self.timetable[day][shift.id].remove(employee)
                self.schedule[employee.id][day] = self.data.shifts.dummy

        self.weekends[employee.id] = [0 for w in range(self.data.weeks)]
        self.available_shifts[employee.id] = [employee.shifts_per_week[w] for w in range(self.data.weeks)]

    def assign_shift(self, employee, shift):
        """ Assign shift to employee. """
        utils.safety_check(self.schedule[employee.id][shift.day].id > -1, "Assigning shift to employee on busy day. ")

        # -- add to timetable and schedule
        self.timetable[shift.day][shift.id].append(employee)
        self.schedule[employee][shift.day].append(shift)

        # -- if shift was on the weekend adjust weekends
        if self.data.is_on_weekend(shift.dat):
            self.weekends[employee.id][shift.week] += 1

        # -- upate count
        self.available_shifts[employee.id][shift.week] -= 1
        utils.safety_check(self.available_shifts[employee.id][shift.week] < 0, "available_shifts is gone negative while assigning shift")

    # WRITE / READ
    def write(self, file_path = ""):
        # -- create string first
        string = "TIMETABLE\n"
        for day in range(self.data.days):
            string += "DAY {0}\n".format(day)
            shifts = self.data.shifts.select(name='*', mandatory='*', day=day, week='*')
            for s in shifts:
                for e in self.data.employees:
                    if not e.unavailable[s] and self.x_var[e][s].Value() > 0:
                        string += "{0}: {1}\n".format(s, e.name)

        string += "\SCHEDULE"
        for e in self.data.employees:
            string += "Employee {0}\n".format(e.name)
            for day in range(self.data.days):
                if self.schedule[e.id][day].id > -1:
                    string += "\t- day {0}: {1}".format(day,self.schedule[e.id][day].name )

        if file_path:
            with open(file_path, 'w') as target:
                target.write(string)
        else:
            print string

    # -- FEASIBILIT CHECKS
    def check_shift_coverage(self):
        """ Checks if every mandatory turn is assigned to an employee"""
        return all(((not s.mandatory) or self.timetable[d][s.id]) for s in self.data.shifts for d in range(self.days) if not self.data.is_holiday[d] )

    def check_adjacency(self):
        """ Checks if employees are assigned to non-adjacent shifts"""
        for e in self.data.employees:
            for day in range(self.data.days -1):
                if self.schedule[e.id][day] and self.schedule[e.id][day + 1]:
                    if self.data.shifts.adjacency_matrix[self.schedule[e.id][day], self.schedule[e.id][day+1]]:
                        print("Adjacency Check Failed! {0} is assigned to {1} on day {2} and on {3} on day {4}".format(e.name,self.schedule[e.id][day].name, day, self.schedule[e.id][day+1].name, day+1))
                        return False
        return True

    def check_shifts_number(self):
        """ Checks if employees work right number of shift"""
        for week in range(self.data.weeks):
            holidays = sum(self.data.is_holiday[week*7:(week+1)*7])
            for employee in self.data.employees:
                vacations = sum(employee.on_vacation[week*7:(week+1)*7])
                shifts_worked = sum(1 for day in range(7) if self.schedule[employee][day + week * 7])
                shifts_to_do = employee.shift_week - vacation - (holidays if employee.ccnl_contract else 0)
                if shifts_to_do != shifts_worked:
                    print("Shifts Check Failed! {0} works {1} shifts instead of {2} in week {3}.".format(employee.name, shifts_worked,shifts_to_do, week))
                    return False
        return True

    def check_unavailabilty(self):
        # TODO
        return True

    def check_vacation(self):
        # TODO
        return True

    def checks_weekend(self):
        """ Checks if any employee has worked more too many weekend in a row"""
        for e in self.data.employees:
            for week in range(self.data.weeks - parameters.max_we_consecutive):
                if all(self.weekends[e.id][w] > 0 for w in range(week, week + parameters.max_we_consecutive)):
                    print("Shifts Check Failed! {0} works {1} consecutive weekends starting on week {2}.".format(e.name, parameters.max_we_consecutive, week))
                    return False
        return True


    def checks_max_shifts(self):
        """ For each type of shifts check that employees respect the max number allowed per week. """
        for shift, bound in parameters.shifts_max_week.items():
            for e in self.data.employees:
                for week in range(self.data.weeks):
                    if sum(self.schedule[e.id][d].id == shift.id for d in range(week*7, (week+1)*7)) > bound:
                        print("Shifts Check Failed! {0} works {1} shifts on week {2}.".format(
                            e.name,sum(self.schedule[e.id][d].id == shift.id for d in range(week*7, (week+1)*7)), bound))
                        return False
        return True

