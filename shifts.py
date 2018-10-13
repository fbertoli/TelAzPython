import parameters
import itertools
from datetime import datetime
import utilities
import collections

''' 
An object is a list of namedtuple (shift).
'''
Shift = collections.namedtuple('Shift', ['name', 'mandatory', 'day', 'week'])


class Shifts(list):
    # -- list with names of shift
    mandatory = list()
    intermediate = list()
    get_shift = dict()  # name,day: shift defined by name and day

    # -- dict containing info for all shifts
    info = dict()  # name shift: dict() -> start: sting, end: sting, mandatory: bool, min_operators: int, number_operators: int, on_days (only for intermediates): list

    # -- matrix identifying adjacent turns
    adjacency_matrix = dict()  # (shift_1, sfhit_2): True iff whenever shift_1 implies shift_2 cannot be taken on the next day

    def read_file(self, days, holidays):
        # -- read file
        with open(parameters.file_turni, 'r') as source:
            lines = source.readlines()

        # -- create shifts info
        reading_mandatory = False
        for line in lines:
            if utilities.similar_string("OBBLIGATORI", line.strip()) > 0.9:
                reading_mandatory = True
            elif utilities.similar_string("INTERMEDI", line.strip()) > 0.9:
                reading_mandatory = False
            else:
                parts = line.lower().split()
                if len(parts) < 3:
                    continue
                name = parts[0]
                self.info[name] = {"start": parts[1], "end": parts[2], "mandatory": reading_mandatory, \
                                   "min_operators": 0, "max_operators": parameters.max_operators, "number_operators": 0, "on_days": list()}

                # -- safety check
                # TODO: safety check for shift reading

                if reading_mandatory:
                    self.mandatory.append(name)
                else:
                    self.info[name]["on_days"] = list(range(7))
                    self.intermediate.append(name)

                i = 3
                while i < len(parts):
                    if utilities.similar_string(parts[i], "minimo_operatori") > .8:
                        i += 2
                        self.info[name]["min_operators"] = int(parts[i])
                    elif utilities.similar_string(parts[i], "massimo_operatori") > .8:
                        i += 2
                        self.info[name]["max_operators"] = int(parts[i])
                    elif utilities.similar_string(parts[i], "numero_operatori") > .8:
                        i += 2
                        self.info[name]["number_operators"] = int(parts[i])
                    elif utilities.similar_string(parts[i], "giorni") > .8:
                        j = i + 2
                        while True:
                            try:
                                self.info[name]["on_days"] = [utilities.days_map[parts[j].replace(",", "")]]
                                j += 1
                            except KeyError:
                                break
                        i = j
                    elif utilities.similar_string(parts[i], "escluso") > .8:
                        j = i + 2
                        while j < len(parts):
                            try:
                                self.info[name]["on_days"].remove(utilities.days_map[parts[j][:3]])
                                j += 1
                            except KeyError:
                                break
                        i = j
                    i += 1

        # -- populate self.shifts
        for i in range(days):
            if not holidays[i]:
                self += [Shift(item, True, i, int(i / 7)) for item in self.mandatory]
                self += [Shift(item, False, i, int(i / 7)) for item in self.intermediate if (i % 7) in self.info[item]["on_days"]]

        # -- populate get_shift
        for s in self:
            self.get_shift[s.name, s.day] = s

    def create_shift_adjacency_matrix(self):
        for s_1, s_2 in itertools.product(self.info.keys(), self.info.keys()):  # use keys() isntead of items() for compatibility with python 2
            # -- create datetime objects for shift 1
            hour, minute = utilities.get_hour_minute(self.info[s_1]["end"])
            shift_1_end_time = datetime(2018, 1, 2, hour, minute)

            if utilities.is_night_shift(s_1, hour): # if s_1 is night shift, set all other turns of next day as adjacent
                self.adjacency_matrix[s_1, s_2] = True
            else:
                # -- create datetime objects for shift 2
                hour, minute = utilities.get_hour_minute(self.info[s_2]["start"])
                shift_2_start_time = datetime(2018, 1, 3, hour, minute)

                # -- check
                # TODO: this might be not considering the extra day in case (giorno, notte). However it should not be a problem.
                t_delta = shift_2_start_time - shift_1_end_time
                self.adjacency_matrix[s_1, s_2] = (t_delta.total_seconds() / 3600) < parameters.min_rest_hours

    """ Filter the list based on the attributes of values passed through kwargs. Value '*' is a wildcard """
    def select(self, **kargs):
        # -- create list of positions and values to compare
        attributes = list()
        values = list()
        for k, v in kargs.items():
            if v != '*':
                attributes.append(k)
                values.append(v)
        return [item for item in self if all(getattr(item, attr) == val for attr, val in zip(attributes, values))]

    """ Return the shifts adjacent to shift. If include_shift is True, the shift passed as argument is included in the 
    returned list. """
    def get_adjacent(self, shift, include_shift=True):
        adjacent = list()
        for other in self:
            if other.day == shift.day:
                if include_shift:
                    adjacent.append(other)
                elif other != shift:
                    adjacent.append(other)
            elif other.day - shift.day == 1 and self.adjacency_matrix[shift.name, other.name]:
                adjacent.append(other)
            elif other.day - shift.day == -1 and self.adjacency_matrix[other.name, shift.name]:
                adjacent.append(other)

        return adjacent

# class Shift:
# 	mandatory = True
# 	name = ""
# 	day = 0
# 	week = 0

# 	def __init__(self, name, mandatory, day, week):
# 		self.mandatory = mandatory
# 		self.name = name
# 		self.day = day
# 		self.week = week

# 	def __eq__(self, other):
# 		return (self.day == other.day) and (self.name == other.name) and (self.mandatory == other.mandatory)

# 	def __ne__(self, other):
# 		return not self.__eq__(other)

# 	def __str__(self):
# 		return "{0}, {1}, {2}, {3}".format(self.name, self.mandatory, self.day, self.week)
