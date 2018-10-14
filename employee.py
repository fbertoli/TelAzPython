import collections

EmployeeTuple = collections.namedtuple('EmployeeTuple', ['name', 'ccnl_contract', 'shifts_per_week', 'unavailable', 'id'])
# name: string
# ccnl_contract: bool
# shifts_per_week:  dict(): int (week) -> number of shifts to do in that week
# unavailable: dict() shift object -> bool


class Employee(EmployeeTuple):
    def __hash__(self):
        return self.id

    def __str__(self):
        string = self.name
        if self.ccnl_contract:
            string += " [ccnl]"
        # if all([item == self.shifts_per_week[0] for item in self.shifts_per_week.values()]):
        #     string += " - shifts per week = {0}".format(self.shifts_per_week[0])
        # else:
        string += " - shifts per week  "
        for w, s in self.shifts_per_week.items():
            string += "{0}: {1}, ".format(w, s)

        # -- print unavailibilities
        unavailibilities = list()
        for k, v in self.unavailable.items():
            if v:
                unavailibilities.append("{0} - {1}".format(k.name, k.day))

        # -- paste strings
        if unavailibilities:
            string += "\nUnavailable on: " + ", ".join(unavailibilities)
        return string

# def employee_to_str(employee):
#     string = employee.name
#     if employee.ccnl_contract:
#         string += " [ccnl]"
#     if all([item == employee.shifts_per_week[0] for item in employee.shifts_per_week.values()]):
#         string += " - shifts per week = {0}".format(employee.shifts_per_week[0])
#     else:
#         string += " - shifts per week = "
#         for w,s in employee.shifts_per_week.items():
#             string += "{0}: {1}".format(w,s)
#
#     # -- print unavailibilities
#     unavailibilities = list()
#     for k, v in employee.unavailable.items():
#         if v:
#             unavailibilities.append("{0} - {1}".format(k.name, k.day))
#
#     # -- paste strings
#     if unavailibilities:
#         string += "\nUnavailable on: " + ", ".join(unavailibilities)
#     return string
