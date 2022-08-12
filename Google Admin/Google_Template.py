## LIBRARY IMPORTS ##############################################
from openpyxl import Workbook
## IMPORT N4S
try:
    from n4s import fs
    n4s_installed = True
except ModuleNotFoundError:
    n4s_installed = False
#################################################################

## MAIN
class GoogleTemplate():

    ## MAIN
    def create():
        template = 'google_template.xlsx'
        if n4s_installed:
            fs.path_exists(f"{fs.root('docs')}/Google Admin", True)
            template = f"{fs.root('docs')}/Google Admin/google_template.xlsx"
        workbook = Workbook()
        Student_Info = workbook.active
        Student_Info["A1"] = "First Name [Required]"
        Student_Info["B1"] = "Last Name [Required]"
        Student_Info["C1"] = "Email Address [Required]"
        Student_Info["D1"] = "Password [Required]"
        Student_Info["E1"] = "Password Hash Function [UPLOAD ONLY]"
        Student_Info["F1"] = "Org Unit Path [Required]"
        Student_Info["G1"] = "New Primary Email [UPLOAD ONLY]"
        Student_Info["H1"] = "Recovery Email"
        Student_Info["I1"] = "Home Secondary Email"
        Student_Info["J1"] = "Work Secondary Email"
        Student_Info["K1"] = "Recovery Phone [MUST BE IN THE E.164 FORMAT]"
        Student_Info["L1"] = "Work Phone"
        Student_Info["M1"] = "Home Phone"
        Student_Info["N1"] = "Mobile Phone"
        Student_Info["O1"] = "Work Address"
        Student_Info["P1"] = "Home Address"
        Student_Info["Q1"] = "Employee ID"
        Student_Info["R1"] = "Employee Type"
        Student_Info["S1"] = "Manager Email"
        Student_Info["T1"] = "Department"
        Student_Info["U1"] = "Cost Center"
        Student_Info["V1"] = "Building ID"
        Student_Info["W1"] = "Floor Name"
        Student_Info["X1"] = "Floor Section"
        Student_Info["Y1"] = "New Status [UPLOAD ONLY]"
        Student_Info["Z1"] = "Advanced Protection Program enrollment"
        workbook.save(template)

    ## MESSAGE ON COMPLETION
    def completed():
        print("\nProcess Completed!\n"
        "For n4s users, the file is located in '/Documents/Google Admin'")

## RUN
GoogleTemplate.create()
GoogleTemplate.completed()