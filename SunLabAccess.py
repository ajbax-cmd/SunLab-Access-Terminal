import mysql.connector 
from mysql.connector import Error
import PySimpleGUI as sg
from datetime import date
from datetime import datetime
import PIL.Image
import time
import re

# connection function: sets up connection to mysql database and returns connection object
def connection():
    try:
        connection = mysql.connector.connect(host='localhost',
                                         database='sunlabaccess',
                                         user='root',
                                         password='password123')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            return connection, cursor, record

    except Error as e:
        print("Error while connecting to MySQL", e)


def validate_ID(id):
    return (len(str(id)) == 9 and type(id) != 'int')


def validate_Dates(value1, value2):
    if(len(value1) != 10 or len(value2) != 10):
        return False
    if(value1[4] != '-' and value1[7] != '-'):
        return False
    if(value2[4] != '-' and value2[7] != '-'):
        return False
    value1 = value1.replace("-", "")
    value2 = value2.replace("-", "")
    try:
        if(int(value1) > int(value2)):
            return False
    except Error as e:
        return False
    return True


def validate_Times(value1, value2):
    return(validate_Times_Helper(value1) and validate_Times_Helper(value2))

def validate_Times_Helper(value):
    if(len(value) > 5): return False
    if(len(value) < 4): return False
    if(len(value) == 5):
        if(value[2] != ":"): return False
        try:
            temp1 = int(value[:2])
            temp2 = int(value[3:])
            if(temp1 < 0): return False
            if(temp1 > 23): return False
            if(temp2 > 59): return False
        except Error as e:
            return False
    else:
        if(value[1] != ":"): return False
        try:
            temp1 = int(value[:1])
            temp2 = int(value[2:])
            if(temp1 < 0): return False
            if(temp1 > 23): return False
            if(temp2 > 59): return False
        except Error as e:
            return False
    return True

def validate_timestamp(val1, val2):
    if(len(val1) != 14 or len(val2) != 14): return False
    sub_str1 = val1[:8]
    sub_str2 = val2[:8]
    sub_str_time1 = val1[8:]
    sub_str_time2 = val2[8:]

    try:
        sub_dt1 = int(sub_str1)
        sub_dt2 = int(sub_str2)
        dt1 = int(val1)
        dt2 = int(val2)

        if(sub_dt1 > sub_dt2): return False
        if(sub_dt1 == sub_dt2):
            if(sub_str_time2 < sub_str_time1):
                return False
    except:
        return False
    return True

def display_table(cursor):
    result = cursor.fetchall()
    layout = [
             [sg.Text("Query Results:")],
             [sg.Table(values=result,
                 headings=[col[0] for col in cursor.description],
                 auto_size_columns=True,
                 display_row_numbers=False,
                 num_rows=min(25, len(result)))]
              ]
    window = sg.Window("Query Results", layout, resizable=True, finalize=True)
    while True:
        event, values = window.read()
        if (event == sg.WIN_CLOSED):
            window.close()
            break


def login(con):
    layout = [[sg.Text(text='Sun Lab Access Terminal',
            font=('Arial Bold', 16),
            size=20, expand_x=True, pad =(0,50),
            justification='center')],
            [sg.Image('penn_state_lion.png', size=(32,32), pad=(0,0),
            expand_x=True, expand_y=True)],
            [sg.Text('User ID: ', justification='center') ],
            [sg.InputText(key='-IN-', do_not_clear=False)],
            [sg.Text('Password: ', justification='center')],
            [sg.InputText(key='pass', do_not_clear=False)],
            [sg.Submit(), sg.Exit(), sg.Button('Simulate Swipes')]
        ]
    window = sg.Window('Sun Lab Access Terminal', layout, size=(600,600), element_justification='c')
    cursor = con.cursor()
    password_enabled = True
    try:
        password_file = open('password.txt', 'r')
        password = password_file.readline().strip('\n')
        password_file.close()
    except:
        password_file = open('password.txt', 'w')
        password_file.write('password123')
        password_file.close()
        password_enabled = False

    while(True):
        event, values = window.read()
        if  (event=="Exit"):
            window.close()
            sys.exit()
        if(event == 'Simulate Swipes'):
            window.close()
            simulate_swipes(con)
            main()

        try:
            if(values['-IN-'] and validate_ID(values['-IN-']) and not password_enabled):
                cursor.execute("SELECT id, authorized_user FROM users WHERE id = %s", (values['-IN-'],));
                result = cursor.fetchone()

                if(result and result[1] == 1):
                    break
                else:
                    sg.popup("Not authorized to access Sun Lab Access Terminal!")
            elif(not validate_ID(values['-IN-'])):
                sg.popup("ID must be a 9 digit number!")
            elif(validate_ID(values['-IN-']) and password_enabled):
                cursor.execute("SELECT id, authorized_user FROM users WHERE id = %s", (values['-IN-'],));
                result = cursor.fetchone()

                if((result and result[1] == 1) and values['pass'] == password):
                    break
                else:
                    sg.popup("Not authorized to access Sun Lab Access Terminal!")

        except Error as err:
                print(f"Error: '{err}'")
    window.close()

def simulate_swipes(con):
    layout = [
            [sg.Text('User ID: ')], 
            [sg.InputText(key= 0, do_not_clear=False) ],
            [sg.Text("Time Stamp In - YYYYMMDDHHMMSS")],
            [sg.InputText(key= 1, do_not_clear=False) ],
            [sg.Text("Time Stamp Out - YYYYMMDDHHMMSS")],
            [sg.InputText(key= 2, do_not_clear=False), ],
            [sg.Submit(), sg.Button('Log In'), sg.Exit()]
           ]
    window = sg.Window('Sun Lab Access Terminal - Simulate ID Card Swipe', layout, size=(600, 300))


    cursor = con.cursor()
    while(True):
        event, values = window.read()
        if (event == sg.WIN_CLOSED or event=="Exit"):
            window.close()
            sys.exit()
        if(event =='Log In'):
            window.close()
            break
        try:
            if(values[0] and validate_ID(values[0])):
                cursor.execute("SELECT id, user_status FROM users WHERE id = %s", (values[0],));
                result = cursor.fetchone()

                if(result and result[1] == 1 and validate_timestamp(values[1], values[2])):
                   cursor.execute("INSERT INTO access values(%s, %s, %s)", (values[0], values[1], values[2]));
                   con.commit()
                   sg.popup("Swipe succesfully added to Sun Lab Access database!")
                elif(not validate_timestamp(values[1], values[2])):
                    sg.popup("Timestamp entered incorrectly, Must follow YYYYMMDDHHMMSS format!")
                elif(not result):
                    sg.popup("Swipe Failed - User ID not found. Please contact a Sun Lab administrator to have your ID activated.")
                else:
                    sg.popup("Swipe Failed - User Id not authorized to access the Sun Lab!")
            else:
                sg.popup("ID must be a 9 digit number!")
        except Error as err:
            print(f"Error: '{err}'")

def main_menu(con):

    window = main_menu_helper()
    while(True):
        event, values = window.read()
        if(event == sg.WIN_CLOSED or event=="Exit"):
            window.close()
            sys.exit()
        elif(event == 'Activate ID'):
            window.close()
            activate_id(con)
            window = main_menu_helper()
        elif(event == 'Suspend ID'):
            window.close()
            suspend_id(con)
            window = main_menu_helper()
        elif(event == 'Reactivate ID'):
            window.close()
            reactivate_id(con)
            window = main_menu_helper()
        elif(event == 'Change Password'):
            window.close()
            change_password()
            window = main_menu_helper()
        else:
            window.close()
            search(con)
            window = main_menu_helper()


def main_menu_helper():
    layout = [[sg.Text(text='Main Menu',
              font=('Arial Bold', 14),
              size=20, expand_x=True, pad =(0,0),
              justification='center')],
              [sg.Button('Activate ID')], 
              [sg.Button('Suspend ID')],
              [sg.Button('Reactivate ID')],
              [sg.Button('Search Access Logs')],
              [sg.Button('Change Password')],
              [sg.Exit()]
             ]

    window = sg.Window('Sun Lab Access Terminal', layout, size=(500, 300))
    return window


def activate_id(con):
     layout = [
            [sg.Text('User ID: ') ],
            [sg.InputText(key='0', do_not_clear=False)],
            [sg.Text('First Name: ')],
            [sg.InputText(key='1', do_not_clear=False)],

            [sg.Text('Last Name: ')],
            [sg.InputText(key='2', do_not_clear=False)],

            [sg.Text('User Type: ')],
            [sg.InputText(key='3', do_not_clear=False)],

            [sg.Checkbox('Authorized to Access Sun Lab', default=False, key="4")],
            [sg.Checkbox('Authorized to Use Sun Lab Access Terminal', default=False, key="5")],
            [sg.Submit(), sg.Button('Main Menu'), sg.Exit()]
       ]
     window = sg.Window('Sun Lab Access Terminal - Activate User ID', layout, size=(600, 300))
     cursor = con.cursor()
     while(True):
         event, values = window.read()
         if(event == sg.WIN_CLOSED or event=="Exit"):
             window.close()
             sys.exit()
         elif(event =='Main Menu'):
             window.close()
             break
         try:
             if(validate_ID(values['0'])):
                cursor.execute("INSERT INTO users values(%s, %s, %s, %s, %s, %s)", (values['0'], values['1'], values['2'], values['3'], values['4'], values['5']));
                con.commit()
                sg.popup("User succesfully added to Sun Lab Access database!")
             else:
                sg.popup("ID must be a 9 digit number!")
         except Error as err:
            print(f"Error: '{err}'")

def suspend_id(con):
     layout = [
            [sg.Text('User ID: ') ],
            [sg.InputText(key='-IN-', do_not_clear=False)],
            [sg.Submit(), sg.Button('Main Menu'), sg.Exit()]
        ]
     window = sg.Window('Sun Lab Access Terminal - Suspend User ID', layout, size=(600, 300))
     cursor = con.cursor()
     while(True):
         event, values = window.read()
         if (event == sg.WIN_CLOSED or event=="Exit"):
             window.close()
             sys.exit()
         elif(event =='Main Menu'):
             window.close()
             break
         try:
             if(validate_ID(values['-IN-'])):
                cursor.execute("SELECT id, user_status FROM users WHERE id = %s", (values['-IN-'],));
                result = cursor.fetchone()
             
                if(result and result[1] == 1):
                    cursor.execute("UPDATE users SET user_status = 0, authorized_user = 0 WHERE id = %s", (values['-IN-'],))
                    con.commit()
                    sg.popup("User access to Sun Lab has been revoked!")
             else:
                sg.popup("ID must be a 9 digit number!")
         except Error as err:
            print(f"Error: '{err}'")


def reactivate_id(con):
    layout = [
            [sg.Text('User ID: ') ],
            [sg.InputText(key='0', do_not_clear=False)],
            [sg.Checkbox('Authorized to Use Sun Lab Access Terminal', default=False, key="1")],
            [sg.Submit(), sg.Button('Main Menu'), sg.Exit()]
        ]
    window = sg.Window('Sun Lab Access Terminal - Reactivate User ID', layout, size=(600, 300))
    cursor = con.cursor()
    while(True):
        event, values = window.read()
        if (event == sg.WIN_CLOSED or event=="Exit"):
            window.close()
            sys.exit()
        elif(event =='Main Menu'):
            window.close()
            break
        try:
            if(validate_ID(values['0'])):
                cursor.execute("SELECT id, user_status FROM users WHERE id = %s", (values['0'],));
                result = cursor.fetchone()
             
                if(result):
                    cursor.execute("UPDATE users SET user_status = 1, authorized_user = %s WHERE id = %s", (values['1'], values['0']))
                    con.commit()
                    sg.popup("User access to Sun Lab has been reinstated!")
            else:
                sg.popup("ID must be a 9 digit number!")
        except Error as err:
            print(f"Error: '{err}'")


def search(con):
    layout = [
            [sg.Text('User ID: '), sg.InputText(key= 0, do_not_clear=False) ],
            [sg.Text("Date - YYYY-MM-DD")],
            [sg.Text('From: '), sg.InputText(key= 1, do_not_clear=False), sg.Text('To: '), sg.InputText(key= 2, do_not_clear=False)],
            [sg.Text("Time - HH:MM")],
            [sg.Text('From: '), sg.InputText(key= 3, do_not_clear=False), sg.Text('To: '), sg.InputText(key= 4, do_not_clear=False)],
            [sg.Submit(), sg.Button('Main Menu'), sg.Exit()]
           ]
    window = sg.Window('Sun Lab Access Terminal - Browse Sun Lab Access Logs', layout, size=(600, 300))


    cursor = con.cursor()
    while(True):
        event, values = window.read()
        if (event == sg.WIN_CLOSED or event=="Exit"):
            window.close()
            sys.exit()
        if(event =='Main Menu'):
            window.close()
            break

        try:
           # 7 possible active states of inputs, 7 possible conditionals
           # 1st case, search by only User ID
            if(values[0] and not values[1] and not values[2] and not values[3] and not values[4]):
                if(validate_ID(values[0])):
                    cursor.execute("SELECT * FROM users NATURAL JOIN access where id = %s", (values[0],))
                    display_table(cursor)
                else:
                    sg.popup("ID must be a 9 digit number!")
           # 2nd case: search by only date
            elif(not values[0] and values[1] and values[2] and not values[3] and not values[4]):
                if(validate_Dates(values[1], values[2])):
                    cursor.execute("SELECT * FROM users NATURAL JOIN access where timestamp_In >= %s and timestamp_Out <= %s", (values[1], values[2]))
                    display_table(cursor)
                else:
                    sg.popup("Dates must be in YYYY-MM-DD format and/or begin date must be earlier than end date!")
           # 3rd case: search by only time
            elif(not values[0] and not values[1] and not values[2] and values[3] and values[4]):
                if(validate_Times(values[3], values[4])):
                    cursor.execute("SELECT * FROM users NATURAL JOIN access where cast(timestamp_In as time) >= %s or cast(timestamp_Out as time) <= %s", (values[3], values[4]))
                    display_table(cursor)
                else:
                    sg.popup("Times must be in HH:MM format!")
           # 4th case: search by ID and date
            elif(values[0] and values[1] and values[2] and not values[3] and not values[4]):
                if(validate_ID(values[0]) and validate_Dates(values[1], values[2])):
                    cursor.execute("SELECT * FROM users NATURAL JOIN access where id = %s and timestamp_In >= %s and timestamp_Out <= %s", (values[0], values[1], values[2]))
                    display_table(cursor)
                else:
                    sg.popup("ID must be a 9 digit number and/or dates must be in YYYY-MM-DD format and/or begin date must be earlier than end date!")
           # 5th case: search by ID and time
            elif(values[0] and not values[1] and not values[2] and values[3] and values[4]):
                if(validate_ID(values[0]) and validate_Times(values[3], values[4])):
                    cursor.execute("SELECT * FROM users NATURAL JOIN access where id = %s and cast(timestamp_In as time) >= %s or cast(timestamp_Out as time) <= %s", (values[0], values[3], values[4]))
                    display_table(cursor)
                else:
                    sg.popup("ID must be a 9 digit number and/or times must be in HH:MM format!")
           # 6th case: search by date and time
            elif(not values[0] and values[1] and values[2] and values[3] and values[4]):
                if(validate_Dates(values[1], values[2]) and validate_Times(values[3], values[4])):
                    dt0 = values[1] + " " + values[3]
                    dt1 = values[2] + " " + values[4]
                    cursor.execute("SELECT * FROM users NATURAL JOIN access where timestamp_In >= %s and timestamp_Out <= %s", (dt0, dt1))
                    display_table(cursor)
                else:
                    sg.popup("Dates must be in YYYY-MM-DD format and/or begin date must be earlier than end date and/or times must be in HH:MM format!")
           # 7th case: search by ID, date, and time
            elif(values[0] and values[1] and values[2] and values[3] and values[4]):
                if(validate_ID(values[0]) and validate_Dates(values[1], values[2]) and validate_Times(values[3], values[4])):
                    dt0 = values[1] + " " + values[3]
                    dt1 = values[2] + " " + values[4]
                    cursor.execute("SELECT * FROM users NATURAL JOIN access where id = %s and timestamp_In >= %s and timestamp_Out <= %s", (values[0], dt0, dt1))
                    display_table(cursor)
                else:
                    sg.popup("ID must be a 9 digit number and/or dates must be in YYYY-MM-DD format and/or begin date must be earlier than end date and/or times must be in HH:MM format!")
           # if only one date or one time were input for any of the above
            else:
               sg.popup("Invalid Input!")

        except Error as err:
            sg.popup(f"Error: '{err}'")

def change_password():
     layout = [
            [sg.Text('New Password: ') ],
            [sg.InputText(key=1, do_not_clear=False)],
            [sg.Text('Repeat Password: ')],
            [sg.InputText(key=2, do_not_clear=False)],
            [sg.Submit(), sg.Button('Main Menu'), sg.Exit()]
        ]
     window = sg.Window('Sun Lab Access Terminal - Suspend User ID', layout, size=(600, 300))
     while(True):
         event, values = window.read()
         if (event == sg.WIN_CLOSED or event=="Exit"):
             window.close()
             sys.exit()
         elif(event =='Main Menu'):
             window.close()
             break
         if(values[1] == values[2]):
            try:
                password_file = open('password.txt', 'w')
                password_file.write(values[1])
                password_file.close()
                sg.popup('Password successfully changed!')
            except Error as err:
                print(f"Error: '{err}'")
         else:
             sg.popup('New password must match repeat password!')


def main():
    con, cursor, record = connection()
    if con.is_connected():
        print('You are connected to database: "', record)

    while(True):
        login(con)
        main_menu(con)

if(__name__ == '__main__'):
    main()