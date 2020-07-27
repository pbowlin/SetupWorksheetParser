# from CoronaTrackerPrograms.Nolde_Input_Manager import Nolde_Input_Manager 
# The above import must be used if I place all corona files inside folder named CoronaTrackerPrograms and then run
# this file from the parent directory as a module with "python3 -m CoronaTrackerPrograms.Auto_Input_Nolde_Remote_Support.py"


from Nolde_Input_Manager import Nolde_Input_Manager
from Credentials_Getter_COVID import get_credentials
import csv


print("\n\n\n\n")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+            Welcome to the Event Input Program                +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

username, password = get_credentials()

with open('MikeSchedule.csv') as file:
	data = csv.DictReader(file)

	manager = Nolde_Input_Manager(data, username, password)
	manager.input_events()

	


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+          Thanks for using the Event Input Program            +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("\n\n\n\n")
