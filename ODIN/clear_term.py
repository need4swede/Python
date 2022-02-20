import platform, os

def clear_term():
        if platform.system() == "Windows":
                clear = lambda: os.system('cls')
                clear()
                print()
        if platform.system() == "Darwin":
                os.system("clear")
                print()