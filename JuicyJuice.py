import os
import csv
import glob
import ctypes
import datetime
import sys
import PySimpleGUI as sg
from pathlib import Path
from dicts import *
from thermal_helper import generate_receipt_image, generate_total_receipt 
from escpos.printer import Usb, Dummy

LANGUAGE = "Arabic" # Default language
W, H = sg.Window.get_screen_size() # Gets the screen size
PASSWORD = "2245" # Password to access the admin panel
ICON = ico

def get_prices(tuple): # Gets the prices of the items in the table
    check_prices_file()
    p = os.path.expanduser(f"~\\Documents\\JuicyJuice\\items.csv")
    f = open(p, 'r', encoding="utf-8-sig")
    item_dict = csv.DictReader(f, delimiter=';')

    for dict in item_dict:
        item = tuple[0].capitalize()
        if dict["Type"] == item:
            f.close()
            return float(dict[tuple[1]].strip())

def reverse_str(string): # Reverses a string
    return " ".join(string.split()[::-1]) 

def cr_fr(fruit="", size=(0,0)): # Creates the frames and buttons of the respective juices
    fruit= fruit.lower()
    fruitname = juice_translation_dict[fruit] if LANGUAGE == "Arabic" else fruit.capitalize()
    img = image_dict[fruit] if fruit in image_dict else black # Check if has valid image
    layout = [[sg.B(image_data=img, k=fruit)],[sg.Text(f"{fruitname}", justification='c')]]
    return sg.Frame("", layout, element_justification='c', size=size)

def cr_drink_btn(name, size, type): # Creates buttons
    name = name.lower()
    current_dict = dicts_dict[type]
    drinkname = reverse_str(current_dict[name]) if LANGUAGE == "Arabic" else name.capitalize()
    return sg.B(drinkname, size=(size, 1), k=name)

def cr_option_btn(name): # Creates the buttons of the size selector window
    text = size_translaction_dict[name] if LANGUAGE == 'Arabic' else name
    return [sg.Button(text, size=(12, 4), k=name)]
    
def table_layout(): # Creates the table element on the left side
    headers = ['Juice Type'.center(15), 'Qty'.center(4), 'Size'.center(4),'Price'.center(6)]
    if LANGUAGE == "Arabic":
        for i in range(len(headers)):
            headers[i] = translaction_dict[headers[i].strip().lower()]
    content = [[]]
    return [[sg.Table(content, headers, expand_y=True, justification="c", k="T", border_width=2,  
                        background_color='white', hide_vertical_scroll=True, text_color='black',
                        enable_events=True, select_mode=sg.TABLE_SELECT_MODE_BROWSE, header_border_width=2)]]

def juices_layout(): # Arranges the juice frames on the middle
    remove_btn_txt = translaction_dict['correct last'] if LANGUAGE == "Arabic" else "Remove last" #I don't have the correct translation for 'Remove last'
    finish_btn_txt = translaction_dict['complete order'] if LANGUAGE == "Arabic" else "Complete"
    finish_btn_txt = reverse_str(finish_btn_txt)
    juices,l = [], []
    w = (W/100)*7.2
    h = (H/100)*11.3
    for fruit in fruit_list:
        if '+' not in fruit:
            l.append(cr_fr(fruit, (w,h)))
        if (len(l) == 3):
            juices.append(l)
            l = []
    return [[sg.Fr("", juices)], [  sg.B(remove_btn_txt, button_color="Red", expand_x=True, k="CRLS", auto_size_button=False), #CRLS = Correct last
                                    sg.B(finish_btn_txt, button_color='Green', expand_x=True, k="CO", auto_size_button=False)]] #CO = Complete Order

def mixtures_layout(): # Arranges the mixture frames on the right side 

    mixtures, l = [], []
    w = (W/100)*12.5
    h = (H/100)*11.3
    for fruit in fruit_list:
        if '+' in fruit:
            l.append(cr_fr(fruit, (w, h)))
        if (len(l) == 3):
            mixtures.append(l)
            l = []
    return [[sg.Fr("", mixtures)], [sg.B(button_text = reverse_str("عصائر أخرى") if LANGUAGE == 'Arabic' else "Other Products", expand_x=True, k='SW1')]]

def cocktails_layout(): # Arranges the secondary column on the right side
    cocktails, l = [], []
    for drink in cocktails_list:
        l.append(cr_drink_btn(drink, 22, 'cocktail'))
        if (len(l) == 3):
            cocktails.append(l)
            l = []

    food_layout = [cr_drink_btn("Fruit salad", 35, 'food'), cr_drink_btn("Ice cream", 35, 'food')]

    return [[sg.Fr("", cocktails,)], food_layout, [sg.B(button_text = reverse_str("عصائر أخرى") if LANGUAGE == 'Arabic' else "Other Products", expand_x=True, k='SW2')]]

def size_selector_layout(): # Creates the layout of the size selector window
    layout = []
    for list_item in size_translaction_dict:
        layout.append(cr_option_btn(list_item))
    return layout

def make_main_win(): # Creates the main aplication window
    p = Path(__file__).with_name('icon.ico')
    layout_l = table_layout()
    layout_m = juices_layout()
    layout_r1 = mixtures_layout()
    layout_r2 = cocktails_layout()
    layout = [ [sg.Column(layout_l, element_justification='center', expand_y=True), 
                sg.VerticalSeparator(color='Black'), 
                sg.Column(layout_m, vertical_alignment='top'),
                sg.VerticalSeparator(color='Black'),
                sg.Column(layout_r1, vertical_alignment='top', k='-RCOL1-'), #Primary right column
                sg.Column(layout_r2, vertical_alignment='top',visible=False, k='-RCOL2-')]] #Alternative right columm

    return sg.Window("Juicy Juice", layout, finalize=True, resizable=True, element_justification='c', icon=ICON)

def make_start_win(): # Creates the window that asks for the sellers name
    layout = [  [sg.Menu([['Show', ['Admin Panel']]], tearoff=False)],
                [sg.T("Enter salesman name:\nأدخل اسم البائع:", font=("Verdana", 12, 'bold')), sg.Sizer(164, 0), sg.B("English", size=(6,1))],
                [sg.In("", focus=True, k="-IN-"), sg.B("عربى", size=(6,1), k="Arabic")]] #TODO change to sg.In(default_text="") 
    return sg.Window("Login", layout, finalize=True, icon=ICON)

def make_admin_win(): # Creates the admin window
    month = datetime.date.today().month
    year = datetime.date.today().year
    day = datetime.date.today().day
    years = [*range(1,99)]
    months = [*range(1,13)]
    days = [*range(1,31)]
    bests, reports  = daily_report(day, f"{month:02}", str(year)[2:4])
            
    layout = [  [sg.Menu([['Options', ['Add Expense', 'Print Report']], ['Show', ['All Expenses', 'Correction Log']]], tearoff=False, key='ADMMENU')],
                [sg.B("Yearly Report", expand_x=True), sg.Sp(years, str(year)[2:4], s=(2,1), k="Year"), 
                 sg.B("Monthly Report", expand_x=True), sg.Sp(months, month, s=(2,1), k="Month"),
                 sg.B("Daily Report", expand_x=True), sg.Sp(days, day, s=(2,1), k="Day")],
                [sg.Table(bests, headings=["Best Salesman", "Most sold item", "Liquid revenue", "Total sales"], num_rows=2, expand_x=True, justification='c', k="BT")], # BT = Best Table
                [sg.Table(reports, headings=["Salesman", "Date", "Item", "Size", "Price"], expand_x=True, expand_y=True, justification='c', k="AT")]] #AT = Admin Table
    return sg.Window("Admin Panel", layout, finalize=True, resizable=True, icon=ICON)

def make_add_expense_win(): # Creates the add expense window
    layout_l = [[sg.T("Expense Type:")],
                [sg.T("Amount (KG):")],
                [sg.T("Price (SAR):")]]
    layout_r = [[sg.In("", size=(20,1), expand_x=True)],
                [sg.Spin([*range(1,999)], initial_value=1)],
                [sg.In('', size =(20,1), expand_x=True)]]
    layout = [  [sg.Column(layout_l, element_justification='r'), sg.Column(layout_r, element_justification='l')],
                [sg.B("Add", size=(10,1)), sg.B("Cancel", size=(10,1))]]
    return sg.Window("Add Expense", layout, element_justification='c', finalize=True, icon=ICON)

def make_all_expenses_win(): # Creates the all expenses window
    year = datetime.date.today().year
    year = str(year)[2:]
    content = get_expenses(year)
    layout = [  [sg.T("Year"), sg.Spin([*range(1,99)], initial_value=year, size=(2,1), k="ExpenseYear"),
                 sg.B("Refresh", size=(8,1)), sg.B("Cancel", size=(8,1))],
                [sg.Table(  content, headings=["Expense Type", "Amount (KG)", "Price (SAR)", " Date "], 
                            expand_x=True, expand_y=True, justification='c',k="ET")]] #ET = Expense Table
    return sg.Window("All Expenses", layout, finalize=False, icon=ICON)

def make_correction_log_win(): # Creates the correction log window
    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Logs\\Correction_Log.csv")
    check_log_file(path)
    content = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            content.append((row["Salesman"], row["Date"], row["Item"], row["Size"]))
    content.reverse()
    layout = [  [sg.Table(content, headings=["Salesman", "Date", "Item", "Size"], expand_x=True, expand_y=True, justification='c', k="CT")]] #CT = Correction Table
    return sg.Window("Correction Log", layout, finalize=True, icon=ICON)

def make_selector_win(): # Creates the size selector window
    sg.theme('Brown blue')
    layout = size_selector_layout()
    return sg.Window('Size Selector', layout, finalize=True, icon=ICON, disable_minimize=True)

def set_quantities(list): # Sets the quantities of the items in the table
    items = {}
    for list_item in list:
        items[list_item] = items.get(list_item, 0) + 1
    return items

def change_table(current_items): # Changes the table according to the current items
    if current_items == []:
        return [[]]
    total_txt = " الإجمالي:" if LANGUAGE == 'Arabic' else "Total:"
    tax_txt = "ضريبة القيمة المضافة:" if LANGUAGE == 'Arabic' else "Tax value:"
    after_tax_txt = "المبلغ الإجمالي  المستحق:" if LANGUAGE == 'Arabic' else "Total after tax:"
    tuple_dict = set_quantities(current_items)
    total_price = 0
    table_items = []
    for item in tuple_dict:
        price = tuple_dict[item]*get_prices(item)
        total_price += price
        name = all_items_dict[item[0]] if LANGUAGE == 'Arabic' else item[0].capitalize()
        size = translaction_dict[shorthand_dict[item[1]].lower()] if LANGUAGE == 'Arabic' else shorthand_dict[item[1]]
        table_items.append((name, tuple_dict[item], size, f"{price:.2f}"))
    table_items.append(("", "", "", ""))
    table_items.append((total_txt,"", "", f"{total_price:.2f}"))
    table_items.append((tax_txt,"", "", f"{total_price*0.15:.2f}"))
    table_items.append((after_tax_txt, "", "" , f"{total_price*1.15:.2f}"))
    return table_items   

def create_invoice(current_items, current_salesman): # Prints the receipt of the current order
    items = change_table(current_items)
    total = 0
    for item in items:
        total += float(item[3])
    print(f"{current_salesman}'s receipt:")
    for item in items:
        print(f"{item[0]} {item[1]} {item[2]} {item[3]}")
    print(f"Total: {total:.2f}")

def check_report_file(path): # Checks if the report file exists, if not, creates it
    paths = os.path.split(path)
    FILE_ATTRIBUTE_HIDDEN = 0x02

    if not os.path.exists(paths[0]):
        os.makedirs(paths[0])
        ctypes.windll.kernel32.SetFileAttributesW(paths[0], FILE_ATTRIBUTE_HIDDEN)
    if not os.path.exists(path) and path[1] != '':
        with open(path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Salesman", "Day", "Item", "Size", "Price"], delimiter=";")
            writer.writeheader()
            ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

def check_expense_file(path): # Checks if the expense file exists, if not, creates it
    paths = os.path.split(path)
    FILE_ATTRIBUTE_HIDDEN = 0x02

    if not os.path.exists(paths[0]):
        os.makedirs(paths[0])
        ctypes.windll.kernel32.SetFileAttributesW(paths[0], FILE_ATTRIBUTE_HIDDEN)
    if not os.path.exists(path) and path[1] != '':
        with open(path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Expense", "Amount", "Price", "Month", "Day"], delimiter=";")
            writer.writeheader()
            ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

def check_log_file(path): # Checks if the log file exists, if not, creates it
    paths = os.path.split(path)
    FILE_ATTRIBUTE_HIDDEN = 0x02

    if not os.path.exists(paths[0]):
        os.makedirs(paths[0])
        ctypes.windll.kernel32.SetFileAttributesW(paths[0], FILE_ATTRIBUTE_HIDDEN)
    if not os.path.exists(path) and path[1] != '':
        with open(path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Salesman", "Date", "Item", "Size"], delimiter=";")
            writer.writeheader()
            ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

def check_prices_file(): # Checks if the prices file exists, if not, creates it
    def create_items_template(): # Creates items.csv template
        p = os.path.expanduser(f"~\\Documents\\JuicyJuice")
        if not os.path.exists(p):
            os.makedirs(p)

        template_path = Path(__file__).with_name('items.csv')
        template = open(template_path, 'r', encoding="utf-8-sig")
        item_dict = csv.DictReader(template, delimiter=';')
        f = open(p + "\\items.csv", "w", newline="", encoding="utf-8-sig")
        writer = csv.DictWriter(f, fieldnames=item_dict.fieldnames, delimiter=';')
        writer.writeheader()

        for row in item_dict:
            writer.writerow(row)

        template.close()
        f.close()
    if not os.path.exists(os.path.expanduser(f"~\\Documents\\JuicyJuice\\items.csv")):
        create_items_template()

def check_printer_file(): # Checks if the printer file exists, if not, creates it
    def create_printer_template():
        p = os.path.expanduser(f"~\\Documents\\JuicyJuice")
        if not os.path.exists(p):
            os.makedirs(p)
        
        f = open(p + "\\printer.txt", "w", newline="", encoding="utf-8-sig")
        f.write("Vendor ID=0x1209\n")
        f.write("Product ID=0x0000\n")
        f.close()
    if not os.path.exists(os.path.expanduser(f"~\\Documents\\JuicyJuice\\printer.txt")):
        create_printer_template()

def log_sale(current_items, current_salesman): # Creates sale log
    month = datetime.date.today().month
    year = datetime.date.today().year
    day = datetime.date.today().day
    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Reports\\SalesReport_{month:02}_{year}.csv")
    check_report_file(path)

    with open(path, mode="a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Salesman", "Day", "Item", "Size", "Price"], delimiter=";")
        for item in current_items:
            writer.writerow({"Salesman": current_salesman, "Day": day, "Item": item[0], "Size": item[1], "Price": get_prices(item)})

def yearly_report(year): # Creates yearly report
    contents = []
    salesmans, items = {}, {}
    total, sales = 0, 0
    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Reports\\")
    expense_path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Expenses\\20{year}_Expenses.csv")
    check_report_file(path)
    for file in glob.glob(path+f"SalesReport_*_20{year}.csv"):
        month = Path(file).stem.split('_')[1]
        with open(file, 'r', encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                contents.append((row["Salesman"], f"20{year}/{month:02}/{row['Day']}", row["Item"].capitalize(), row["Size"], f"{float(row['Price']):05.2f}"))
                salesmans[row["Salesman"]] = salesmans.get(row["Salesman"], 0) + 1
                items[row["Item"]] = items.get(row["Item"], 0) + 1
                sales += 1
                total += float(row["Price"])
    check_expense_file(expense_path)
    with open(expense_path, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            total -= float(row["Price"])
    try:
        bests = [[max(salesmans, key=salesmans.get), max(items, key=items.get).capitalize(), total, sales]]
    except:
        bests = []
    return bests, contents

def month_report(month, year): # Creates monthly report
    contents = []
    salesmans, items = {}, {}
    total, sales = 0, 0
    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Reports\\")
    expense_path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Expenses\\20{year}_Expenses.csv")
    check_report_file(path)
    file = path + f"SalesReport_{month:02}_20{year}.csv"
    if not os.path.exists(file):
        return [], []
    with open(file, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            contents.append((row["Salesman"], f"20{year}/{month:02}/{row['Day']}", row["Item"].capitalize(), row["Size"], f"{float(row['Price']):05.2f}"))
            salesmans[row["Salesman"]] = salesmans.get(row["Salesman"], 0) + 1
            items[row["Item"]] = items.get(row["Item"], 0) + 1
            sales += 1
            total += float(row["Price"])
    check_expense_file(expense_path)
    with open(expense_path, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row["Month"] == str(month):
                total -= float(row["Price"])
    try:
        bests = [[max(salesmans, key=salesmans.get), max(items, key=items.get).capitalize(), total, sales]]
    except:
        bests = []
    return bests, contents

def daily_report(day, month, year): # Creates daily report
    contents = []
    salesmans, items = {}, {}
    total, sales = 0, 0
    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Reports\\")
    expense_path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Expenses\\20{year}_Expenses.csv")
    check_report_file(path)
    file = path + f"SalesReport_{month:02}_20{year}.csv"
    if not os.path.exists(file):
        return [], []
    with open(file, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row["Day"] == str(day):
                contents.append((row["Salesman"], f"20{year}/{month:02}/{row['Day']}", row["Item"].capitalize(), row["Size"], f"{float(row['Price']):05.2f}"))
                salesmans[row["Salesman"]] = salesmans.get(row["Salesman"], 0) + 1
                items[row["Item"]] = items.get(row["Item"], 0) + 1
                sales += 1
                total += float(row["Price"])
    check_expense_file(expense_path)
    with open(expense_path, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row["Day"] == str(day) and row["Month"] == str(month):
                total -= float(row["Price"])
    try:
        bests = [[max(salesmans, key=salesmans.get), max(items, key=items.get).capitalize(), total, sales]]
    except:
        bests = []
    return bests, contents

def add_expense(expense, amount, price): # Adds expense to the expenses file
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Expenses\\{year}_Expenses.csv")
    check_expense_file(path)
    with open(path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Expense", "Amount", "Price", "Month", "Day"], delimiter=";")
        writer.writerow({"Expense": expense, "Amount": amount, "Price": price, "Month": month, "Day": day})

def get_expenses(year): # Gets all expenses from the year's expenses file
    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Expenses\\20{year:02}_Expenses.csv")
    check_expense_file(path)
    with open(path, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        expenses = []
        for row in reader:
            expenses.append((row["Expense"], row["Amount"], row["Price"], f"{int(row['Month']):02}/{row['Day']}"))
    return expenses

def log_correction(item, salesman): # Logs corrected items
    date_hour_minute = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    path = os.path.expanduser(f"~\\AppData\\Local\\JuicyJuice\\Logs\\Correction_Log.csv")
    check_log_file(path)
    with open(path, 'a', encoding="utf-8-sig", newline='') as f:
        writer = csv.DictWriter(f, ["Salesman", "Date", "Item", "Size"], delimiter=';')
        writer.writerow({"Salesman": salesman, "Date": date_hour_minute, "Item": item[0].capitalize(), "Size": item[1]})

def get_item(data): # Parse item from table
    if LANGUAGE == "Arabic":
        arabic_to_english = {}
        for english, arabic in all_items_dict.items():
            arabic_to_english[arabic] = english
        juice_type = arabic_to_english[data[0]]
        juice_size = shorthand_dict[arabic_to_english[data[2]].upper()]
    else:
        juice_type = data[0].lower()
        juice_size = shorthand_dict[data[2]]
    return (juice_type, juice_size)

def is_valid_num(num): # Checks if the input is a valid float
    try:
        float(num)
        return True
    except ValueError:
        return False

def create_invoice(items, salesman, payment_method): # Create invoice receipt
    p = os.path.expanduser(f"~\\Documents\\JuicyJuice\\")
    tuple_dict = set_quantities(items)
    table_items = []
    for item in tuple_dict:
        price = tuple_dict[item]*get_prices(item)
        name = item[0].capitalize()
        quantity = tuple_dict[item]
        table_items.append({"item_name": name, "price": price, "quantity": quantity})
    im = generate_receipt_image(payment_method, table_items, salesman)
    try:
        print_receipt(im)
    except:
        im.save(p+"invoice.jpg", dpi = (300, 300))

def create_report(items): # Creates report receipt
    p = os.path.expanduser(f"~\\Documents\\JuicyJuice\\")
    items_dict = []
    for item in items:
        items_dict.append({'total': float(item[4]), 'date': item[1]})
    im = generate_total_receipt(items_dict)
    try: 
        print_receipt(im)
    except:
        im.save(p+"report.jpg", dpi = (300, 300))

def print_receipt(image):
    check_printer_file()
    p = os.path.expanduser(f"~\\Documents\\JuicyJuice\\printer.txt")
    
    with open(p, 'r') as f:
        vendorid = f.readline().split("=")[1].strip()
        productid = f.readline().split("=")[1].strip()
    p = Usb(vendorid, productid)
    d = Dummy()

    d.image(image)
    d.cut()

    p._raw(d.output()) 

def Main():
    global LANGUAGE 
    current_items = []
    item_to_remove = ''
    payment_method = ''
    sg.theme('Blue Mono')
    sg.set_options(font=("Verdana", 10))

    window = make_start_win()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # Closes the window
            break
        elif event in ("English", "Arabic"): # Changes the language
            if values['-IN-'] == "": # If the user doesn't enter a salesman
                _ , _ = sg.Window("Error", [[sg.Text("The seller name must be entered\nيجب ادخال اسم البائع", justification='c')], 
                                            [sg.Ok()]], element_justification='center', icon=ICON).read(close=True)
                continue         
            salesman_name = values['-IN-'] 
            LANGUAGE = event
            window.close()
            window = make_main_win()
            window.maximize() 
            break
        elif event == "Admin Panel": # Opens the admin panel
            event, values = sg.Window("Admin Panel", [[sg.Text("Enter Password"), sg.Input(password_char='*', size=(15, 1))], 
                                                      [sg.Ok(bind_return_key=True), sg.Cancel()]], element_justification='center',
                                                      icon=ICON).read(close=True)
            if event == "Ok":
                if values[0] == PASSWORD:
                    window.close()
                    window = make_admin_win()
                    window.maximize()
                    break
                else:
                    _ , _ = sg.Window("Error", [[sg.Text("Wrong Password", justification='c')], 
                                                [sg.Ok()]], element_justification='center', icon=ICON).read(close=True)


    win2_active = False

    while True:
        rmv_last_txt = reverse_str("تعديل الطلب") if LANGUAGE == "Arabic" else "Remove last" 
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED: # Closes the window
            sys.exit()
            break
        # Events of the main window

        elif event in ("SW1", "SW2"): # Switches between the two right columns
            window['-RCOL1-'].update(visible = not window["-RCOL1-"].visible)
            window['-RCOL2-'].update(visible = not window["-RCOL2-"].visible)

        elif event == "CRLS": # Corrects the last item in the table and create correction log
            if len(current_items) == 0:
                _ , _ = sg.Window("Error", [[sg.Text(text = "لايوجد عناصر للتعديل" if LANGUAGE =='Arabic' else "No items to correct",
                                                     justification='c')], 
                                            [sg.B(button_text = translaction_dict['ok'] if LANGUAGE == 'Arabic' else 'Ok')]], 
                                            element_justification='center', icon=ICON, disable_minimize=True).read(close=True)
                continue
            else:
                text = "هل أنت متأكد؟ سيؤدي ذلك إلى إنشاء سجل تصحيح جديد" if LANGUAGE == 'Arabic' else "Are you sure? This will create a new correction log"
                option, _ = sg.Window("Correction", [[sg.T(text=text)],
                                                [sg.Yes(), sg.No()]], element_justification='center', icon=ICON, disable_minimize=True).read(close=True)
                if option == 'No':
                    continue
                if item_to_remove != '':
                    current_items.remove(item_to_remove)
                    removed_item = item_to_remove
                    window["CRLS"].update(rmv_last_txt)
                    item_to_remove = ''
                else:
                    removed_item = current_items.pop()
                log_correction(removed_item, salesman_name)
                window['T'].update(values=change_table(current_items))

        elif event == "CO": # Finishes the order and prints the receipt
            
            if len(current_items) == 0:
                title = "خطأ" if LANGUAGE == 'Arabic' else "Error"
                _ , _ = sg.Window(title, [[sg.Text(text = "لايوجد عناصر مطلوبة" if LANGUAGE == 'Arabic' else "No items ordered",
                                                     justification='c')], 
                                            [sg.B(button_text = translaction_dict['ok'] if LANGUAGE == 'Arabic' else 'Ok')]], 
                                            element_justification='center', icon=ICON, disable_minimize=True).read(close=True)
                continue
            else:
                cash = "نقدي" if LANGUAGE == 'Arabic' else "Cash"
                card = "بطاقة" if LANGUAGE == 'Arabic' else "Card"
                title = "طريقة الدفع او السداد" if LANGUAGE == 'Arabic' else "Payment Method"
                payment, _ = sg.Window(title, [[ sg.B(cash, s=(15,2), k='Cash'),
                                                            sg.B(card, s=(15,2), k='Card')]],
                                                            element_justification='center', icon=ICON, disable_minimize=True).read(close=True)
                if payment not in ("Cash", "Card"):
                    continue
                window["CRLS"].update(rmv_last_txt)
                payment_method = payment
                create_invoice(current_items, salesman_name, payment_method)
                item_to_remove = ''
                log_sale(current_items, salesman_name)
                window["T"].update(values=[])
                current_items = []
        
        elif event == "T": # When something is clicked on the table
            if values["T"] == []:
                continue
            data = window["T"].get()[values[event][0]] #Gets text from selected row
            if data[0].lower() not in all_items_dict:
                item_to_remove = ''
                window["CRLS"].update(rmv_last_txt)
                continue
            item_to_remove = get_item(data)
            window["CRLS"].update(text="تصحيح" if LANGUAGE == "Arabic" else "Correct")

        # Events of the admin panel

        elif event == "Yearly Report": # Prints the yearly report
            bests, reports = yearly_report(values['Year'])
            window['BT'].update(values=bests)
            window['AT'].update(values=reports)
            window.refresh()

        elif event == "Monthly Report": # Prints the monthly report
            bests, reports = month_report(values['Month'], values['Year'])
            window['BT'].update(values=bests)
            window['AT'].update(values=reports)
            window.refresh()
        
        elif event == "Daily Report": # Prints the daily report
            bests, reports = daily_report(values['Day'], values['Month'], values['Year'])
            window['BT'].update(values=bests)
            window['AT'].update(values=reports)
            window.refresh()
        
        elif event == "Add Expense": # Adds an expense to the database
            option, values = make_add_expense_win().read(close=True)
            if option == "Cancel":
                continue
            elif option == "Add" and values[0] != "" and values[1] != "" and values[2] != "" and is_valid_num(values[2]) :
                add_expense(values[0], values[1], values[2])
            else :
                _ , _ = sg.Window("Error", [[sg.Text("Invalid input", justification='c')], 
                                            [sg.Ok()]], element_justification='center', icon=ICON).read(close=True)
            
        elif event == "All Expenses" and not win2_active: # Creates window that shows all expenses
            window2 = make_all_expenses_win()
            win2_active = True

        elif win2_active: # Display window that reads all the expenses
            option, values = window2.read(timeout=100)

            if option in (sg.WIN_CLOSED, "Cancel"):
                win2_active = False 
                window2.close()
            elif option == "Refresh":
                window2['ET'].update(values=get_expenses(values['ExpenseYear']))
                window2.refresh()     

        elif event == "Correction Log":
            _, _ = make_correction_log_win().read(close=True)
        
        elif event == "Print Report":
            items = window["AT"].get()
            if items == []:
                continue
            create_report(items)
                

        elif event == "__TIMEOUT__": # If the window timesout, the loop continues
            continue

        else: # Deals with all buttons
            window["CRLS"].update(rmv_last_txt)
            item_to_remove = ''
            selection, _ = make_selector_win().read(close=True)
            if selection in (sg.WIN_CLOSED, "__TIMEOUT__"):
                continue
            if (event, selection) == ("fruit salad", "Small"):
                continue 
            current_items.append((event, selection))
            try :
                window["T"].update(values=change_table(current_items))
            except:
                break
            window.refresh()

if __name__ == "__main__":
    Main()       