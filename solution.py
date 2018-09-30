import data as dataModule


class Solution:
	data = None
	timetable = dict() ## shift object: list of employees assigned on shift
	schedule = dict() ## employee object: dict() -> day: shift object  (note one shift per day is allowed)

	def __init_-(self, data):
		self.data = data
		self.schedule = {employee: {day: None for day in range(data.days)} for employee in data.employees}
		self.timetable = {shift: list() for shift in data.shifts}

	## chek if every mandatory turn is assigned to an employee
	def check_shift_coverage(self):
		return all((k.mandatory and v) for k,v in self.timetable.items())


	## check if employees are assigned to non-adjacent shifts
	def check_adjacency(self):
		for employee in self.data.employees:
			for day in range(self.data.days -1):
				if self.schedule[employee][day] and self.schedule[employee][day + 1]:
					if self.data.shifts.adjacency_matrix[self.schedule[employee][day], self.schedule[employee][day+1]]:
						print("Adjacency Check Failed! {0} is assigned to {1} on day {2} and on {3} on day {4}".format(employee.name,self.schedule[employee][day].name, day, self.schedule[employee][day+1].name, day+1))
						return False
		return True

	## check if employess work right number of shift
	def check_shifts(self):
		for week in range(self.data.days / 7):
			holidays = sum(self.data.holidays[week*7:(week+1)*7])
			for employee in self.data.employees:
				if employee.ccnl_contract:
					shifts = sum(1 for day in range(7) if self.schedule[employee][day + week*7])
					if shifts != employee.shift_week - holidays:
						print("Shifts Check Failed! {0} works {1} shifts in week {3} which has {4} days of holiday.".format(employee.name, shifts, week, holidays))
						return False
				else:
					shifts = sum(1 for day in range(7) if self.schedule[employee][day + week*7])
					if shifts != employee.shift_week:
						print("Shfts Check Failed! {0} works {1} shifts in week {3}.".format(employee.name, shifts, week))
						return False
		return True



