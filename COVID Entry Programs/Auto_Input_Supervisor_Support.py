from Supervisor_Support_Input_Manager import Supervisor_Support_Input_Manager
from Credentials_Getter_COVID import get_credentials
import csv


print("\n\n\n\n")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+            Welcome to the Event Input Program                +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

username, password = get_credentials()

with open('SupervisorReport.csv', encoding='latin-1') as file:
	data = csv.DictReader(file)

	manager = Supervisor_Support_Input_Manager(data, username, password)
	manager.input_events()

	


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+          Thanks for using the Event Input Program            +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("\n\n\n\n")
