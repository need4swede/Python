import platform, os

## CLEAR TERMINAL
def clear(self):
    if platform.system() == "Windows":
            clear = lambda: os.system('cls')
            clear()
            print()
    if platform.system() == "Darwin":
            os.system("clear")
            print()