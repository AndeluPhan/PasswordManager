import psycopg2
import psycopg2.extras
import time
import datetime
import re
import hashlib
import os
from cryptography.fernet import Fernet

def formatString(wordVal):
    wordVal = wordVal.lower()
    wordVal = wordVal.strip()
    return wordVal

#to activate the virtual environment. cd in to Password_safe and type "pass\Scripts\activate"
cryptKey = b'npV7wQljsuMUNVct-yYsm9xYwHZZFOyk5hJTxCpQMkw=' #will be used later to encrypt the passwords stored in the database
cipher_suite = Fernet(cryptKey)

#If it's the user's first time, make them make a password to access password manager
if os.path.getsize("text.txt") == 0:
    print("Hello, this seems to be your first time here. Create a password and write it down somewhere. Memorize it. Keep it safe.\n")
    print("This password will be used for your password manager to gain access. Later features will be implemented for password recovery.\n")
    passMatch = True
    while passMatch:
        password = input("Type your password: ")
        password = password.strip()
        password2 = input("Confirm your password: ")
        password2 = password2.strip()
        if password2 != password:
            print("Your password don't match. Try again. \n")
            continue
        passMatch = False
    str2hash = password2
    result = hashlib.md5(str2hash.encode())
    write = result.hexdigest()
    f = open("text.txt", "w")
    f.write(write)
    f.close()
    
#Ask for password to login into to password manager.
Entry = True
while Entry: 
    str2hash = input("Please enter password to gain access to manager: ")
    str2hash = str2hash.strip()
    result = hashlib.md5(str2hash.encode())
    result = result.hexdigest()
    f = open("text.txt", "r")
    encryptedPass = f.readline()
    encryptedPass = formatString(encryptedPass)
    if encryptedPass == result:
        print("\n")
        break
    else:
        print("Your password was incorrect try again!\n")


print("Welcome to the Andrew's Password Manager. '\h' for help or type 'quit' at any time to quit or backtrack")

ts = time.time();
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S');

conn = psycopg2.connect(
    host="localhost",
    database="",
    user="postgres",
    password="" #Insert your own password here                 <----------------
)

#Handle commands

quit = False
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
while not quit:
    Operation = input("What is your operation?: (Print/Create/Read/Update/Delete) or (P/C/R/U/D): ")
    Operation = formatString(Operation)
    if Operation == '\h':
        print("\nPrint: for printing out all passwords you have for. Ex: Bank and Google\n")
        print("Create: for creating new password entries in the password manager\n")
        print("Read: for reading the password in existing password entries in the password manager\n")
        print("Update: for updating existing password entries in the password manager\n")
        print("Delete: for deleting existing password entries in the password manager\n\n")
        continue
        
    if Operation == 'quit':
        quit = True
        continue
    
    # PRINT
    if Operation == 'print' or Operation == 'p':
        print("\nYou currently have passwords stored for the following: \n")
        cur.execute("SELECT * FROM passwords")
        List = cur.fetchall()
        for i in List:
            print(i['for_what'])
        print()

    #READ
    if Operation == 'read' or Operation == 'r':
        notFound = True
        while notFound: 
            purpose = input("What was your password for?: ")
            purpose = formatString(purpose)
            if purpose == "quit": 
                break
            sql = "SELECT * FROM passwords WHERE for_what = %s"
            purpose = (purpose,)
            cur.execute(sql, purpose)
            if cur.rowcount == 0:
                print("We couldn't find what you were looking for..Try Again\n")
                continue
            purpose = ''.join(purpose)
            ciphered_text = bytes(cur.fetchone()["password"])
            unciphered_text = cipher_suite.decrypt(ciphered_text)
            unciphered_text = unciphered_text.decode()
            print("Your password for " + purpose + " is: " + unciphered_text + "\n\n")
            answer = ""
            while answer.lower() != 'y' and answer != 'n':
                answer = input("Would you like to look at another password?: (Y/N)\n")
            if answer.lower() == 'y': continue;
            else: break

    #DELETE
    
    elif Operation == 'delete' or Operation == 'd':
        notFound = True
        while notFound: 
            purpose = input("What was your password for?: ")
            purpose = formatString(purpose)
            if purpose == "quit": 
                break
            sql = "SELECT * FROM passwords WHERE for_what = %s"
            purpose = (purpose,)
            cur.execute(sql, purpose)
            if cur.rowcount == 0:
                print("We couldn't find what you were looking for..Try Again\n")
                continue
            answer = input("We found the password for " + ''.join(purpose) + ", are you sure you want to delete it? (Y/N): ")
            answer = formatString(answer)
            if answer.lower() == 'y':
                sql = "DELETE FROM passwords WHERE for_what = %s"
                cur.execute(sql,purpose);
                print("The password for " + ''.join(purpose) + " has been deleted.\n")
                # cur.execute("SELECT * FROM passwords")
                # print(cur.fetchall())
            else: break  
    #UPDATE COMMAND

    elif Operation == 'update' or Operation == 'u':
        notFound = True
        while notFound: 
            purpose = input("What was your password for?: ")
            purpose = formatString(purpose)
            if purpose == "quit": 
                break
            sql = "SELECT * FROM passwords WHERE for_what = %s"
            purpose = (purpose,)
            cur.execute(sql, purpose)
            if cur.rowcount == 0:
                print("We couldn't find what you were looking for..Try Again\n")
                continue
            answer = input("We found the password for " + ''.join(purpose) + ", are you sure you want to update it? (Y/N): ")
            if answer.lower() == 'y':
                passCheck = True;
                while passCheck: 
                    password = input("Choose your new password: ")
                    password = password.strip()
                    if password == "quit": break
                    if " " in password:
                        print("Space cannot be allowed inside a password.\n")
                        continue
                    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{5,20}$"
                    pat = re.compile(reg)
                    mat = re.search(pat, password)
                    if not mat:
                        print("All passwords must have length between 5-20, a special symbol, at least 1 number, and both upper and lowercase letters\n")
                        continue;
                    passCheck = False
                purpose = ''.join(purpose)
                password = str.encode(password)
                password = cipher_suite.encrypt(password)
                cur.execute("UPDATE passwords SET password = %s, created_on = %s WHERE for_what = %s", (password, timestamp, purpose))
                unciphered_text = cipher_suite.decrypt(password)
                unciphered_text = unciphered_text.decode()

                print("The password for " + ''.join(purpose) + " has been updated to " + unciphered_text + "\n")
            elif answer.lower() == 'n':
                print("You selected no. Please tell us which password to update or type (quit): \n") 
            else: break



    #CREATE COMMANDs
    elif Operation == 'create' or Operation == 'c':
        create = True
        while create: 
            for_what = input("For what is this password for?: ")
            for_what = formatString(for_what)
            if for_what == "quit": break;
            print("All passwords must have length between 5-20, a special symbol, at least 1 number, and both upper and lowercase letters\n")
            passCheck = True;
            while passCheck: 
                password = input("Type your password: ")
                password = password.strip()
                if password == "quit": break
                if " " in password:
                    print("Space cannot be allowed inside a password.\n")
                    continue
                reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{5,20}$"
                pat = re.compile(reg)
                mat = re.search(pat, password)
                if not mat:
                    print("All passwords must have length between 5-20, a special symbol, at least 1 number, and both upper and lowercase letters\n")
                    continue;
                passCheck = False
            # cur.execute("CREATE TABLE passwords (id SERIAL PRIMARY KEY, password VARCHAR (100) NOT NULL, for_what VARCHAR (50) NOT NULL, created_on TIMESTAMP NOT NULL);")        #Create table
            
            #Encryption Process:
            password = str.encode(password)
            password = cipher_suite.encrypt(password)

            
            cur.execute("INSERT INTO passwords (password,for_what,created_on) VALUES(%s,%s,%s);",(password,for_what,timestamp))                #Insert into table
            unciphered_text = cipher_suite.decrypt(password)
            unciphered_text = unciphered_text.decode()
            print("The Password for " + for_what + " is set to " + unciphered_text)
            # cur.execute("SELECT * FROM passwords")
            # print(cur.fetchall())
            conn.commit()
            answer = ""
            while answer.lower() != 'y' and answer != 'n':
                answer = input("Would you like to add another password entry?: (Y/N)\n")
            if answer.lower() == 'y': create = True
            else: break                                                                   
cur.close()
conn.close()
f.close()
print("Thank you for using Andrew's Password Manager");
#List changes. 

