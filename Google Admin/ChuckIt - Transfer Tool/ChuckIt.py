## LIBRARY IMPORTS ##############################################
import shutil, os, os.path, platform, time, shutil
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import Tk
import numpy as np
import pandas as pd
##################################################################
## TERMINAL SIZE
os.system('mode con: cols=200 lines=30')
## CLEAR TERMINAL
def clear_term():
    if platform.system() == "Windows":
        clear = lambda: os.system('cls')
        clear()
        print()
    elif platform.system() == "Darwin":
        os.system("clear")
        print()    
## EXCEL COLUMN TEMPLATES
def column_templates():
    global columns_template
    global columns_template_school
    columns_template = 'First Name [Required],Last Name [Required],Email Address [Required],Password [Required], Password Hash Function [UPLOAD ONLY], Org Unit Path [Required], New Primary Email [UPLOAD ONLY], Recovery Email, Home Secondary Email, Work Secondary Email, Recovery Phone [MUST BE IN THE E.164 FORMAT], Work Phone, Home Phone, Mobile Phone, Work Address, Home Address, Employee ID, Employee Type, Employee Title, Manager Email, Department, Cost Center, Building ID, Floor Name, Floor Section, Change Password at Next Sign-In, New Status [UPLOAD ONLY], Advanced Protection Program enrollment\n'
    columns_template_school = columns_template = 'School, First Name [Required],Last Name [Required],Email Address [Required],Password [Required], Password Hash Function [UPLOAD ONLY], Org Unit Path [Required], New Primary Email [UPLOAD ONLY], Recovery Email, Home Secondary Email, Work Secondary Email, Recovery Phone [MUST BE IN THE E.164 FORMAT], Work Phone, Home Phone, Mobile Phone, Work Address, Home Address, Employee ID, Employee Type, Employee Title, Manager Email, Department, Cost Center, Building ID, Floor Name, Floor Section, Change Password at Next Sign-In, New Status [UPLOAD ONLY], Advanced Protection Program enrollment\n'
    columns_template_export = 'First Name [Required],Last Name [Required],Email Address [Required],Password [Required], Password Hash Function [UPLOAD ONLY], Org Unit Path [Required], New Primary Email [UPLOAD ONLY], Status [READ ONLY], Last Sign In [READ ONLY], Recovery Email, Home Secondary Email, Work Secondary Email, Recovery Phone [MUST BE IN THE E.164 FORMAT], Work Phone, Home Phone, Mobile Phone, Work Address, Home Address, Employee ID, Employee Type, Employee Title, Manager Email, Department, Cost Center, 2sv Enrolled [READ ONLY], 2sv Enforced [READ ONLY], Building ID, Floor Name, Floor Section, Email Usage [READ ONLY], Drive Usage [READ ONLY], Total Storage [READ ONLY], Change Password at Next Sign-In, New Status [UPLOAD ONLY], Advanced Protection Program enrollment\n'
## MAIN FUNCTION
def main():
    start = True
    global user_query
    global query_dir_path
    global template

    # TITLE SCREEN / SELECT INPUT
    while start == True:
        print("****************************************************************")
        print(" ChuckIt, in /The Bucket - The Google Admin Bulk Transfer Tool")
        print("****************************************************************\n")
        print("AUTHOR:")
        print("\n Need4Swede"
        "\n https://github.com/need4swede/\n")
        print("PURPOSE:")
        print("\n",
        "This tool was designed to automate the documentation formatting necessary to single out students who have 'Never logged in' and place them all into a seperate organizational unit for bulk edits.\n")
        print("FUNCTION:\n"
        "\n The application takes an export of Google users as input and automatically formats it and inserts appropriate student information.\n",
        "Headers are organized such to match Google's template, Advanced Protection Program enrollment is disabled for all students,\n",
        "students with log-in activity are excluded from final survey, and the end user is prompted to provide a destination org unit ('/The Bucket' if left blank) alongside a password.\n",
        "Multiple verification checks are conducted to ensure the data is formulated accurately and that it meets the necessary standard for Google Admin.\n")
        print("CONTACT:\n",
        "\n For questions and inquiries, contact theneed4swede@gmail.com\n")

        input("\n\n\nPress any key to continue...")
        print("\nPROMPT - Open user query:")
        win = Tk() # Opens Windows Explorer window w/ import option to choose a downloaded user query
        win.configure(bg='black')
        win.attributes('-transparentcolor', 'black')
        win.attributes('-topmost',1, '-disabled', 0, '-fullscreen', 1)
        filename = askopenfilename()
        win.destroy()
        user_query = filename
        query_dir_path = os.path.dirname(os.path.realpath(user_query))
        query_dir_path = query_dir_path + "/" + "dir"
        start == False
        break
        
    ## FUNCTION SEQUENCE
    set_parameters() # Designate a password and org unit    
    copy_userquery() # Make a copy of the input file to ammend
    edit_userquery() # Make the necessary changes to the copy
    save_userquery() # Save the copy as the output file
    cleanup() # Remove temporary files
## SET DEFAULT PASSWORD AND DESTINATION ORG UNIT
def set_parameters():
    global password
    global destination_org
    password = input("\nSet default password for all students who have never signed in to this: ")
    destination_org = input("Destination org unit you want all of these students transferred to: ")
    if destination_org == "":
        destination_org = "The Bucket"
    destination_org = "/" + destination_org
## DUPLICATES USER_DOWNLOAD.CSV > USER_DOWNLOAD_COPY.CSV
def copy_userquery():
    global user_query_copy
    file_name = os.path.basename(user_query)
    if '.csv' not in file_name:
        clear_term()
        print("Incorrect file format! Google exports are in .csv format.")
        print("The file you chose:", file_name)
        input("Press any key to exit...")
        exit()
    src=(user_query)
    dst=(user_query.replace(file_name, "User_Download_Copy.csv"))
    try:
        user_query_copy = shutil.copy(src,dst)
    except(shutil.SameFileError):
        pass
        print(file_name)
        exit()
    print("\nFILE - Made copy of " + file_name + " to ammend: ")
    print(user_query_copy)
    print()
## SORT USER_DOWNLOAD_COPY.CSV BY 'NEVER LOGGED IN'
## DELETE ALL ROWS THAT DO NOT INCLUDE 'NEVER SIGNED IN'
def edit_userquery():
    # CHECK IF IT'S THE CORRECT FILE AND SORT BY LAST SIGN IN
    df = pd.read_csv(   
        user_query_copy)
    try:         
        df.sort_values(['Last Sign In [READ ONLY]'],
                        axis=0,
                        ascending=[False], 
                        inplace=True)
        df.to_csv(user_query_copy, index=False)
    except(KeyError):
        clear_term()
        if os.path.exists(user_query_copy):
            os.remove(user_query_copy)
        print("\nThe file you chose is not a valid user export. Please run the export again from Google Admin and run the tool.\n")
        input("Press any key to exit...")
        exit()
    # SELECT ONLY !='NEVER LOGGED IN' AND SET ALL ROWS UNDER 'STATUS' TO 'DROP'
    # REMOVE ALL ROWS WHERE 'STATUS' INCLUDES 'DROP'
    df = pd.read_csv(user_query_copy)
    df.loc[~df['Last Sign In [READ ONLY]'].str.contains('Never logged in'), 'Status [READ ONLY]'] = 'DROP'
    df['Status [READ ONLY]'].replace('DROP', np.nan, inplace=True)
    df.dropna(subset=['Status [READ ONLY]'], inplace=True)
    df.to_csv(user_query_copy, index=False)

    # REMOVE UNNECESSARY COLUMNS
    df = pd.read_csv(user_query_copy)
    df.drop('Status [READ ONLY]', inplace=True, axis=1)
    df.drop('Last Sign In [READ ONLY]', inplace=True, axis=1)
    df.drop('2sv Enrolled [READ ONLY]', inplace=True, axis=1)
    df.drop('2sv Enforced [READ ONLY]', inplace=True, axis=1)
    df.drop('Email Usage [READ ONLY]', inplace=True, axis=1)
    df.drop('Drive Usage [READ ONLY]', inplace=True, axis=1)
    df.drop('Total Storage [READ ONLY]', inplace=True, axis=1)
    df.to_csv(user_query_copy, index=False)

    # REMOVE DATA FROM CHANGE PASSWORD AND ADVANCED
    df = pd.read_csv(user_query_copy)
    df.loc[0,'Change Password at Next Sign-In'],df.loc[0::,'Change Password at Next Sign-In']=df['Change Password at Next Sign-In'].values[-1],''
    df.loc[0,'Advanced Protection Program enrollment'],df.loc[0::,'Advanced Protection Program enrollment']=df['Advanced Protection Program enrollment'].values[-1],''
    df.to_csv(user_query_copy, index=False)

    # ADD PASSWORD TO PASSWORD FIELD
    df_pass = password
    df = pd.read_csv(user_query_copy)
    df['Password [Required]'] = df['Password [Required]'].replace('****', np.nan)
    df['Password [Required]'] = df['Password [Required]'].fillna(df_pass)
    df.to_csv(user_query_copy, index=False)

    # REPLACE ALL ORG UNITS WITH THE CHOSEN DESTINATION
    df_org_ = '/'
    org_num = input("Amount of unique org units in your export: ")
    org_num = int(org_num)
    x = 1
    org_list = []
    for x in range(1, org_num+1):
        df_org_x = input("Name of org unit #" + str(x) + ": ")
        if df_org_ in df_org_x:
            df_org_x = df_org_x.replace("/", "")
        df_org_unit = df_org_ + df_org_x
        org_list.append(df_org_unit)
        df['Org Unit Path [Required]'] = df['Org Unit Path [Required]'].replace(df_org_unit, np.nan)
    print("\nYou selected the following org units: ", end="")
    print(org_list)
    input("\nPress any key to continue...")
    df['Org Unit Path [Required]'] = df['Org Unit Path [Required]'].fillna(destination_org)
    df.to_csv(user_query_copy, index=False)
## SAVE OUTPUT FILE
def save_userquery():
    file_exists = os.path.exists(user_query_copy)
    if file_exists == True:
        # COPY USER_COPY.CSV TO CHOSEN DIRECTORY
        print("\nPROMPT - Choose an output directory")
        Tk().withdraw()
        global outputdir
        outputdir = askdirectory()
        src=(user_query_copy)
        user_export = user_query_copy[:user_query_copy.rindex('U')] + 'users_ChuckIt.csv'
        shutil.copy(src,user_export)
        shutil.copy(user_export,outputdir)
        time.sleep(1)
        os.remove(user_export)

        ## CLEAR TERMINAL
        if platform.system() == "Windows":
            clear = lambda: os.system('cls')
            clear()
            print()
        elif platform.system() == "Darwin":
            os.system("clear")
            print()

        print("\nTask Completed Successfully!\n")
        print("FILE - 'users_ChuckIt.csv' saved to ", outputdir + "\n\n")
        input("Press any key to exit...")
## DELETE USER_QUERY_COPY
def cleanup():
    if os.path.exists(user_query_copy):
        os.remove(user_query_copy)
    
        

        



main()
