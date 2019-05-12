"""Update csv files with stock prices or display total stock value since tracking began.
.csv files are of the format yyyy-mm-dd,amount_held,price_at_date. File name is
ticker_code.csv. For example, VAS.AX, the ticker code for VAS on the ASX, would
have a file called VAS.AX.csv.
    - Keep in mind that this ticker code format seems
      to be inconsistent with other websites (i.e. many will have ASX:VAS),
      so be sure to check the ticker is correct for yahoo finance.
"""
import glob
import argparse

from datetime import datetime
from collections import OrderedDict

from yahoo_fin.stock_info import get_live_price
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np
from pandas.plotting import register_matplotlib_converters

def get_amount_held(filename: str):
    """Looks at last line, takes that to be the amount held for today"""
    current_file = open(filename, "r")
    lines = current_file.readlines()
    last_line = lines[len(lines) - 1]
    last_line = last_line.split(",")
    current_file.close()
    return last_line[1]


def check_date(filename: str):
    """Checks to see if already updated today."""
    current_file = open(filename, "r")
    lines = current_file.readlines()
    last_line = lines[len(lines) - 1]
    last_line = last_line.split(",")
    today = datetime.today()
    string_date = today.strftime("%Y-%m-%d")
    if last_line[0][0:10] == string_date[0:10]:
        return 1
    return 0

def update():
    """Adds new line to each file with the update value for the given stock.
    Does not do anything if it has already updated it today
    """
    for filename in glob.glob("*.csv"):
        if check_date(filename): # Ensures only once per day
            return
        ticker = filename[:-4]
        today = datetime.today()
        string_to_append = today.strftime("%Y-%m-%d")
        string_to_append = string_to_append + "," \
                                        + get_amount_held(filename) + "," \
                                        + str(round(get_live_price(ticker), 3)) \
                                        + "\n"
        file_to_append = open(filename, "a+")
        file_to_append.write(string_to_append)
        file_to_append.close()


def display():
    """Reads all .csv files in current working directory, adds the values from
    all stocks for each date, plots the total value to date in line graph
    """
    date_to_vals = OrderedDict()
    dates = []
    values = []
    for filename in glob.glob("*.csv"):
        current_file = open(filename, "r")
        lines = current_file.readlines()
        for line in lines:
            line = line.rstrip()
            sections = line.split(",")
            date_object = datetime.strptime(sections[0], '%Y-%m-%d')
            if date_object not in dates:
                dates.append(date_object)
            if sections[0] not in date_to_vals:
                date_to_vals[sections[0]] = \
                        (float(sections[1]) * float(sections[2]))
            else:
                date_to_vals[sections[0]] += \
                        (float(sections[1]) * float(sections[2]))
        current_file.close()
    for key in date_to_vals.keys():
        values.append(date_to_vals[key])

    fig, ax = plt.subplots()
    ax.plot(dates, values)
    my_fmt = DateFormatter("%d-%m-%Y")
    ax.xaxis.set_major_formatter(my_fmt)

    """
    mpl_dates = matplotlib.dates.date2num(dates)
    print(mpl_dates)
    graph = plt.plot_date(mpl_dates, values, 'bo-')
    graph.xaxis.set_major_formatter(myFmt)

    """
    plt.show()


def main():
    """Check arguments, if "-u" is passed in, run update(), else if "-d" is
    passed run display()
    """
    argparser = argparse.ArgumentParser(description="Update stocks.")
    argparser.add_argument("-u", action="store_true",\
            help="Update mode: Update the value of stocks")
    argparser.add_argument("-d", action="store_true",\
            help="Display mode: Display the value of stocks")
    args = argparser.parse_args()
    if args.u:
        print("update mode")
        update()
    elif args.d:
        print("display mode")
        display()
    else:
        argparser.print_help()

if __name__ == "__main__":
    register_matplotlib_converters()
    main()
