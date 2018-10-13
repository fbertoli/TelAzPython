import collections

Employee = collections.namedtuple('Employee', ['name', 'ccnl_contract', 'shifts_week', 'unavailable'])
# shifts_week:  is number of shift emplyee has to work on a given week
# unavailable: dict() shift -> bool

# class Employee:
# 	def __init__(self):
# 		self.name = ""
# 		self.shifts_week = 0
# 		self.ccnl_contract = False
# 		# days_unavailable = list() # -- i: bool
# 		self.unavailable = dict() # -- shift object: bool


def employee_to_str(employee):
    string = employee.name
    if employee.ccnl_contract:
        string += " [ccnl]"
    string += " - shifts per week = {}".format(employee.shifts_week)

    # -- print unavailibilities
    unavailibilities = list()
    for k, v in employee.unavailable.items():
        if v:
            unavailibilities.append("{0} - {1}".format(k.name, k.day))

    # -- paste strings
    if unavailibilities:
        string += "\nUnavailable on: " + ", ".join(unavailibilities)
    return string
