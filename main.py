#!env/bin/python3
import pygsheets
import sys
import csv

valid = {"yes": True, "y": True, "ye": True,
         "no": False, "n": False}


def read_csv(ifile):

    with open(ifile) as file:
        reader = csv.reader(file, delimiter=',', quotechar='|')

        rows = []
        for row in reader:
            rows.append(row)
        return rows


def yn_prompt(prompt):
    while True:
        sys.stdout.write(prompt)
        choice = input().lower()
        if choice in valid:
            break
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
    return choice


def new_sheet(choice):
    if valid[choice]:
        while True:
            sys.stdout.write("Name of Google Sheet: ")
            choice = input().lower()
            if choice != "":
                break
            else:
                sys.stdout.write(
                    "Please respond with a name for the Google Sheet.\n")
        return choice
    else:
        return None


def main(ifile, ofile):

    gc = pygsheets.authorize(
        outh_file="client_secret.json",
        outh_nonlocal=True)

    all_sheets = gc.list_ssheets()
    all_names = [sheet['name'] for sheet in all_sheets]

    sheet_name = None
    if ofile is None:
        choice = yn_prompt("Do you want to create a new sheet? [y/n] ")
        sheet_name = new_sheet(choice)

    if sheet_name is not None:
        gc.create(sheet_name)
    elif ofile is not None and sheet_name is None:
        sheet_name = ofile
    else:
        while True:
            sys.stdout.write("Name of Google Sheet: ")
            sheet_name = input().lower()
            if sheet_name != "" and sheet_name in all_names:
                break
            elif sheet_name not in all_names:
                choice = yn_prompt(
                    "That sheet does not exist. Try creating a new one? [y/n] ")
                if valid[choice]:
                    sheet_name = new_sheet(choice)
                    gc.create(sheet_name)
                    break
            else:
                sys.stdout.write(
                    "Please respond with the name of the Google Sheet.\n")

    sh = gc.open(sheet_name)
    wks = sh.sheet1
    to_insert = read_csv(ifile)
    for row in to_insert:

        rows = len(wks.get_col(1, returnas='cell', include_empty=False))
        wks.append_row(start=("A" + str(rows + 1)),
                       end=None, values=row)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Wrong number of arguments\nUsage: python auth.py <CSV filename> <Google spreadsheet name>")
    elif len(sys.argv) == 2:
        # Input CSV filename, Output Google Spreadsheet name
        main(sys.argv[1], None)
    else:
        # Input CSV filename, Output Google Spreadsheet name
        main(sys.argv[1], sys.argv[2])
