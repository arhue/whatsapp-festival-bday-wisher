import gspread
import datetime
from webwhatsapi import WhatsAPIDriver
import time
import pickledb 

bday_db = pickledb.load('bday.db', False)
fest_db = pickledb.load('fest.db', False)

driver = WhatsAPIDriver(username="varun",client="chrome")

from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('sheets-1-c8e63906723e.json', scope)
gc = gspread.authorize(credentials)

def get_date_today(i, give_year):
    d = datetime.date.today()
    if give_year is False:
        return(str(int(d.day)-i) + "-" + str(d.month))
    else:
        return(str(int(d.day)-i) + "-" + str(d.month) + "-" + str(d.year))

def get_bday_spread(date_today):
    worksheet = gc.open_by_key('1D7R5eydzMBCvh2hDBhaofodMOU5YlRbUHkDY33DcorM').get_worksheet(0)
    try:
        datecell = worksheet.find(date_today)
    except:
        raise RuntimeError
    list_of_bdays=worksheet.cell(datecell.row, datecell.col+1).value.split(":")
    list_of_bdays[:] = [item for item in list_of_bdays if item != '']
    if not list_of_bdays or '' in list_of_bdays:
        raise ValueError
    return(list_of_bdays)

def get_festivals_spread(date_today):
    worksheet_fest = gc.open_by_key('1HsEKvtjIwK9OoqLi01BjnaKPytXy_omR6EFBYUxX2UQ').get_worksheet(0)
    try:
        datecell = worksheet_fest.find(date_today)
    except:
        raise RuntimeError
    festival=worksheet_fest.cell(datecell.row, datecell.col+1).value
    print(festival)
    if festival is '' or festival is ' ':
        raise ValueError
    return(festival)

def get_all_contacts():
    try:
        all_contacts=driver.get_all_chat_ids()
    except:
        raise RuntimeError
    if not all_contacts:
        raise ValueError
    all_contacts = [j for j in all_contacts if not ('@g.us' in j)]
    return(all_contacts)

def bday_db_retrieve(full_date_contact):
    return bday_db.get(full_date_contact)

def bday_db_reset(full_date_contact):
    bday_db.set(full_date_contact, None)
    bday_db.dump()

def bday_set(full_date_contact):
    bday_db.set(full_date_contact, True)
    bday_db.dump()

def fest_db_retrieve(full_date_contact):
    return fest_db.get(full_date_contact)

def fest_db_reset(full_date_contact):
    fest_db.set(full_date_contact, None)
    fest_db.dump()

def fest_set(full_date_contact):
    fest_db.set(full_date_contact, True)
    fest_db.dump()

def wish_bday(i, contact):
    if i is 0:
        wish = "Hey! Happy bday. Enjoy! 😀"
    else:
        wish = "Hey! Belated wishes on your bday " + str(i) + " days back 😀. Sorry couldn't wish you then. Was caught up with something."
    try:
        driver.send_message_to_id(contact, wish)
    except:
        raise RuntimeError

def wish_fest(i, contact, fest_today):
    if i is 0:
        wish = "Hey! Happy " + str(fest_today) + ". Enjoy! 😀"
    else:
        wish = "Hey! Belated wishes on " + str(fest_today) + " " + str(i) + " days back 😀. Sorry couldn't wish you then. Was caught up with something."
    try:
        driver.send_message_to_id(contact, wish)
    except:
        raise RuntimeError

time.sleep(10)

try:
    all_contacts=get_all_contacts()
except RuntimeError:
    print("Can't retrieve data from Whatsapp. Please try again.")
    quit()
except ValueError:
    print("List is empty. Please try again.")
    quit()

print(all_contacts)

#for bdays
for i in range(0, 7):
    date_today = get_date_today(i, give_year=False)
    print(date_today)
    full_date_today = get_date_today(i, give_year=True)
    print(full_date_today)
    #for bday
    try:
        bdays_today = get_bday_spread(date_today)
    except ValueError:
        print("Nothing in column")
        continue
    except RuntimeError:
        print("No bdays on", date_today)
        continue

    print(bdays_today)

    for contact in all_contacts:
        for number in bdays_today:
            if number in contact:
                full_date_contact = full_date_today + "_" + contact
                print(bday_db_retrieve(full_date_contact))
                #bday_db_reset(full_date_contact)
                if bday_db_retrieve(full_date_contact) is None:
                    try:
                        wish_bday(i, contact)
                    except RuntimeError:
                        print("Runtime error occured while sending messages. Please try again.")
                        quit()
                    bday_set(full_date_contact)

#for festivals
for i in range(0, 7):

    date_today = get_date_today(i, give_year=False)
    print(date_today)
    full_date_today = get_date_today(i, give_year=True)
    print(full_date_today)
    try:
        fest_today = get_festivals_spread(date_today)
    except ValueError:
        print("Nothing in column")
        continue
    except RuntimeError:
        print("No festivals on", date_today)
        continue
    for contact in all_contacts:
        full_date_contact = full_date_today + "_" + contact
        print(fest_db_retrieve(full_date_contact))
        #fest_db_reset(full_date_contact)
        if fest_db_retrieve(full_date_contact) is None:
            try:
                wish_fest(i, contact, fest_today)
            except RuntimeError:
                print("Runtime error occured while sending messages. Please try again.")
                quit()
            fest_set(full_date_contact)
