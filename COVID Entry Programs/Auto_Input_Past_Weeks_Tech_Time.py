from Past_Weeks_Tech_Time_Input_Manager import Past_Weeks_Tech_Time_Input_Manager
from Credentials_Getter_COVID import get_credentials
import csv


print("\n\n\n\n")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+            Welcome to the Event Input Program                +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

username, password = get_credentials()

with open('WeeklyReport.csv', encoding='latin-1') as file:
	data = csv.DictReader(file)

	manager = Past_Weeks_Tech_Time_Input_Manager(data, username, password)
	manager.input_events()

	


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+          Thanks for using the Event Input Program            +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("\n\n\n\n")
