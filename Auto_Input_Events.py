from Events_Input_Manager import Events_Input_Manager
from Credentials_Getter import get_credentials


print("\n\n\n\n")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+            Welcome to the Event Input Program                +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

username, password = get_credentials()

events_file = open("Generated Files/Events List.txt", "r")
events_raw_text = events_file.readlines()

if events_raw_text[4] == "*** PROGRAM LOCK - AFTER CHECKING THIS FILE, DELETE THIS LINE TO ALLOW THE EVENT INPUT PROGRAM TO RUN ***\n": 
	print('File lock has not been removed. Before running this program you must first review the "Events List.txt" file in the generated files folder and then delete the program lock on line 5.')
else:
	manager = Events_Input_Manager(events_raw_text, username, password)
	manager.input_events()


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+          Thanks for using the Event Input Program            +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("\n\n\n\n")
