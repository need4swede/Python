# BACKUP YOUR HALO INFINITE SAVEGAME DATA
# UTILITY CREATED BY NEED4SWEDE
# https://github.com/need4swede

import shutil, os, getpass, platform, time
import tkinter
from tkinter import Tk
from tkinter.filedialog import askdirectory

## CLEAR TERMINAL
if platform.system() == "Windows":
    clear = lambda: os.system('cls')
    clear()
    print()

username = getpass.getuser()
util_log_dir = r"C:\Users\\" + username + r"\AppData\Local\HaloSaveGameUtility"
util_log_file = r"C:\Users\\" + username + r"\AppData\Local\HaloSaveGameUtility\halosavegamelog.txt"

if not os.path.exists(util_log_dir):
    os.makedirs(util_log_dir)
if not os.path.exists(util_log_dir + "\\halosavegamelog.txt"):
    util_log = open(util_log_dir + "\\halosavegamelog.txt", 'w')
    util_log.close()
  
def quit_button():
    global tkTop
    tkTop.destroy()
 
def backup_button():
    # Backup savegame to chosen directory
    with open(util_log_file) as f:
        if not os.stat(util_log_file).st_size == 0:
            lines=f.readlines()
            if 'SystemAppData' in lines[0]:
                savedir = lines[0].rstrip()
                backup_location = lines[1].rstrip()
        else:
            win = Tk()
            
            win.configure(bg='black')
            win.attributes('-transparentcolor', 'black')
            win.attributes('-topmost',1, '-disabled', 0, '-fullscreen', 1)
            savedir = askdirectory(parent=win,
                                            initialdir=r"C:\Users\\" + username + "\AppData\Local\Packages",
                                            title="Please select your Halo 'SystemAppdata' directory")
            win.destroy()
                
            win = Tk()

            win.configure(bg='black')
            win.attributes('-transparentcolor', 'black')
            win.attributes('-topmost',1, '-disabled', 0, '-fullscreen', 1)
            backup_location = askdirectory(parent=win,
                                            initialdir=username,
                                            title="Select a directory to backup your savegame to")
            win.destroy()
                
            with open(util_log_dir + "\\halosavegamelog.txt", 'w') as util_log:
                util_log.write(savedir)
                util_log.write("\n")
                util_log.write(backup_location)
                util_log.close()
        
    for x in range(1000000):
        path = backup_location + r"\\savegame" + str(x)
        isFile = os.path.isdir(path)
        if isFile == True:
            pass
        else:
            if 'SystemAppData' not in savedir:
                os.remove(util_log_file)
                print("You did not pick the correct folder. Please run the backup again and select the 'SystemAppData' directory!")
                exit()
                break
            else:
                shutil.copytree(savedir, backup_location + r"\\savegame" + str(x))
                break
    
def restore_button():
    # Restore savegame from chosen directory
    if os.stat(util_log_file).st_size == 0:
        print("No previous backup found!")
    else:
        with open(util_log_file) as f:
            lines=f.readlines()
            savedir = lines[0].rstrip()
            backup_location = lines[1].rstrip()
            win = Tk()

            win.configure(bg='black')
            win.attributes('-transparentcolor', 'black')
            win.attributes('-topmost',1, '-disabled', 0, '-fullscreen', 1)
            restore_backup = askdirectory(parent=win,
                                            initialdir=backup_location,
                                            title="Please select backup to restore")
            win.destroy()

            print("Save: ", savedir, "\nBackup: ", restore_backup)
            if os.path.exists(savedir +"/Helium"):
                shutil.rmtree(savedir +"/Helium")
            if os.path.exists(savedir +"/wgs"):
                shutil.rmtree(savedir +"/wgs")
            time.sleep(1)
            shutil.copytree(restore_backup, savedir+ "/", dirs_exist_ok=True)


 

tkTop = tkinter.Tk()
tkTop.geometry('300x300') #360 x 360 window
tkTop.title("Halo Savegame Utility")
 
varLabel = tkinter.IntVar()
tkLabel = tkinter.Label(textvariable=varLabel, )
varLabel.set("by Need4Swede")
tkLabel.pack()
 
button1 = tkinter.IntVar()
button1state = tkinter.Button(tkTop,
    text="BACKUP",
    command=backup_button,
    height = 4,
    width = 8,
)
button1state.pack(side='top', ipadx=10, padx=10, pady=15)
 
button2 = tkinter.IntVar()
button2state = tkinter.Button(tkTop,
    text="RESTORE",
	command=restore_button,
    height = 4,
    width = 8,
)
button2state.pack(side='top', ipadx=10, padx=10, pady=15)
 
tkButtonQuit = tkinter.Button(
    tkTop,
    text="QUIT",
    command=quit_button,
    height = 4,
    width = 8,
)
 
tkButtonQuit.pack(side='top', ipadx=10, padx=10, pady=15)
tkinter.mainloop()
