# coding=utf-8
import os
import sys
from datetime import date
import utilities

# -- GLOBAL VARIABLES
# -- files di input
file_turni = ""
file_festivita = ""
file_operatori = ""

# -- key dates
start_date = None
end_date = None

# -- parameters for rules
max_operators = 100
shifts_max_week = dict()    # shift name -> max shifts of this type per week
min_rest_hours = 0          # minimum of hours between two shifts
max_we_consecutive = 1      # max weekend in a row an employee can work

# -- parse the config file
def read_config(file_config="input/config.txt"):
    global start_date, end_date
    global file_turni, file_festivita, file_operatori
    global min_rest_hours, shifts_max_week, max_we_consecutive

    # -- sanity check
    if not os.path.isfile(file_config):
        sys.exit("File di configurazione non esists. Si dovrebbe trovare nella cartelle input sotto il nome config.txt")

    # -- read file
    with open(file_config, 'r') as source:
        lines = source.readlines()

    # -- parse file
    warnings = list()
    for line in lines:
        if "file turni" in line:
            file_turni = line.split("=")[-1].lstrip().rstrip()
            if not os.path.isfile(file_turni):
                warnings.append("file turni non esiste.")

        elif "file festivita" in line:
            file_festivita = line.split("=")[-1].lstrip().rstrip()
            if not os.path.isfile(file_festivita):
                warnings.append("file festivita non esiste.")

        elif "file operatori" in line:
            file_operatori = line.split("=")[-1].lstrip().rstrip()
            if not os.path.isfile(file_operatori):
                warnings.append("file operatori non esiste.")

        elif "minimo ore tra due turni" in line:
            try:
                min_rest_hours = int(line.split("=")[-1])
            except ValueError:
                warnings.append("minimo ore tra due turni non è un numero intero.")

        elif "giorno iniziale" in line:
            date_string = line.split("=")[-1]
            if date_string.count('/') != 2:
                warnings.append("Date devono essere in formato giorno/mese/ora con carattere /.")
            else:
                day, month, year = date_string.split('/')
                start_date = date(utilities.format_year(year), int(month), int(day))
                if start_date.weekday() != 0:
                    warnings.append("Il giorno iniziale non è un Lunedi.")

        elif "giorno finale" in line:
            date_string = line.split("=")[-1]
            if date_string.count('/') != 2:
                warnings.append("Date devono essere in formato giorno/mese/ora con carattere /.")
            else:
                day, month, year = date_string.split('/')
                end_date = date(utilities.format_year(year), int(month), int(day))
                if end_date.weekday() != 6:
                    warnings.append("Il giorno finale non è una Domenica.")

        elif "weekend di fila consentiti" in line:
            try:
                max_we_consecutive = int(line.split("=")[-1])
            except ValueError:
                warnings.append("weekend di fila consentiti non è un numero intero.")

        # TODO: read shifts_max_week

    # -- print warnings
    if warnings:
        print "Ci sono errori nell'uso."
        for item in warnings:
            print "- ", item
        sys.exit()
