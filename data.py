from datetime import date, timedelta
import parameters
import shifts as shiftsModule
import employee as employeeModule
import sys
import utilities


class Data:
    start_date = None  # date object (Must be a monday)
    end_date = None  # date object (Must be a sunday)
    days = 0
    weeks = 0
    holidays = list()  # [i] = whether day start_date + i is holiday
    employees = list()
    shifts = shiftsModule.Shifts()
    days_map = dict()  # (only for printing) i: date object, date object: i
    employee_shift_per_week = dict() # employee, week -> int (number of shifts to do in that week)

    def __init__(self):
        self.start_date = parameters.start_date
        self.end_date = parameters.end_date
        self.days = (self.end_date - self.start_date).days + 1
        for i in range(self.days):
            self.days_map[i] = self.start_date + timedelta(i)
            self.days_map[self.start_date + timedelta(i)] = i
        self.weeks = int(self.days / 7)
        self.holidays = [False for i in range(self.days)]  # i: whether day start_date + i is holiday
        self.read_holidays()
        self.shifts.read_file(len(self.holidays), self.holidays)
        self.shifts.create_shift_adjacency_matrix()
        self.read_employees()
        self.compute_number_of_shifts_per_week()

    def read_holidays(self):
        with open(parameters.file_festivita, 'r') as source:
            lines = source.readlines()

        for line in lines:
            try:
                day, month, year = [int(item) for item in line.split()[0].split('/')]
            except IndexError:
                continue
            # -- make sure format is correct
            delta = date(utilities.format_year(year), month, day) - self.start_date
            if 0 <= delta.days < self.days:
                self.holidays[delta.days] = True

    def read_employees(self):
        # -- read file
        with open(parameters.file_operatori, 'r') as source:
            lines = source.readlines()

        # try:
        i = 0
        while i < len(lines):
            if lines[i].strip():
                name = lines[i].rstrip().lstrip()
                i += 1
                
                # -- ccnl contract
                ccnl_contract = False
                if "ccnl" in lines[i]:
                    ccnl_contract = True
                    i += 1

                # -- identify shifts per week
                if "turni per settimana" not in lines[i]:
                    if utilities.similar_string("turni per settimana", lines[i].split('=')[0]) < .6:
                        sys.exit(
                            "Errore in file operatori. Per operatore {0} manca riga per definire turni per settimana".format(
                                employee.name))
                    else:
                        print("Warning!! Possibili errori di battiture in riga {0}: {1}".format(i, lines[i]))
                shifts_week = int(lines[i].rstrip().split('=')[-1])
                i += 1

                # -- create Employee
                employee = employeeModule.Employee(name, ccnl_contract, shifts_week,
                                                   {shift: False for shift in self.shifts})
                self.employees.append(employee)

                # -- identify optional lines
                while lines[i].strip():
                    try:
                        keyword, value = lines[i].rstrip().split('=')
                    except ValueError:
                        sys.exit("Errore. In", lines[i], "ci sono troppi =. Ce ne dovrebbe esere solo 1.")

                    if "giorni non disponibile" == keyword.rstrip().lstrip():
                        for v in value.split(','):
                            # -- safety check
                            utilities.safety_check(v.count('/') == 2,
                                                  "Data nel formato sbagliato in riga \"giorni non disponibile\" per operatore %s" % employee.name)

                            # -- get date and transform it in day number
                            day, month, year = v.split('/')
                            delta = date(utilities.format_year(year), int(month), int(day)) - self.start_date

                            # -- if day is in range considered, update employee.unuavailable
                            if 0 <= delta.days < self.days:
                                for shift in self.shifts.select(day=delta.days):
                                    employee.unavailable[shift] = True

                    elif "turni non disponibile" == keyword.rstrip().lstrip():
                        for v in value.split(','):
                            # -- safety check
                            utilities.safety_check(v.count('-') == 1, "Formato sbagliato in riga \"turni non disponibile\" per operatore %s" % employee.name)
                            shift_name, shift_day = v.split('-')

                            # -- safety check
                            utilities.safety_check(shift_day.count('/') == 2, "Data nel formato sbagliato in riga \"turni non disponibile\" per operatore %s" % employee.name)

                            # -- get date and transform it in day number
                            day, month, year = shift_day.split('/')
                            delta = date(utilities.format_year(year), int(month), int(day)) - self.start_date

                            # -- if day is in range considered, update employee.unuavailable
                            if 0 <= delta.days < self.days:
                                self.employees[-1].unavailable[
                                    self.shifts.get_shift[shift_name.lstrip().rstrip(), delta.days]] = True

                    elif 'turni specifici' == keyword.rstrip().lstrip():
                        # -- re-set unavailable
                        for k in self.employees[-1].unavailable.keys():
                            self.employees[-1].unavailable[k] = True

                        for v in value.split(','):
                            # -- safety check
                            utilities.safety_check(v.count('-') == 1,
                                                  "Formato sbagliato in riga \"turni specifici\" per operatore %s" % employee.name)
                            shift_name, weekday = v.split('-')

                            # -- update all associate shifts
                            for day in range(utilities.days_map[weekday.strip()[:3]], self.days, 7):
                                if not self.holidays[day]:
                                    self.employees[-1].unavailable[
                                        self.shifts.get_shift[shift_name.lstrip().rstrip(), day]] = False
                    else:
                        keywords = ["turni specifici", "turni non disponibile", "giorni non disponibile"]
                        best_option = keywords[
                            max(enumerate(keywords), key=lambda x: utilities.similar_string(x[1], keyword))[0]]
                        sys.exit(
                            "Opzione non riconosciuta in opzione: \"{0}\". Forse intendevi \"{1}\"?".format(keyword,
                                                                                                            best_option))

                    i += 1
            i += 1

    def compute_number_of_shifts_per_week(self):
        # TODO pre-process the number of shifts per week per employee
        for employee in self.employees:
            for w in range(0, self.days / 7):
                self.employee_shift_per_week[employee, w] = employee.shifts_week

    # except Exception as e:
    # 	print("Errore in file", parameters.file_operatori)
    # 	sys.exit(e)
