from Events_Input_Manager import Events_Input_Manager
from Credentials_Getter import get_credentials
from Event_Checker_GUI import Event_Checker_GUI


print("\n\n\n\n")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+            Welcome to the Event Input Program                +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

username, password = get_credentials()

events_list_filepath = "Generated Files/Events List.txt"

# events_file = open("Generated Files/Events List.txt", "r")
# events_raw_text = events_file.readlines()

GUI = Event_Checker_GUI(events_list_filepath, username, password)
GUI.run_checker_GUI()

if not GUI.closed_with_x:
	GUI.follow_up_event_checker_GUI()

if GUI.run_event_input:
	manager = Events_Input_Manager(events_list_filepath, username, password)
	manager.input_events()


print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("+          Thanks for using the Event Input Program            +")
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("\n\n\n\n")
