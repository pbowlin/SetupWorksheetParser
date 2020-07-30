

def get_credentials():
	try:
		credentials_file = open("Generated Files/Credentials.txt", "r")
		credentials = credentials_file.readlines() 
		username = credentials[2][10:-1]
		password = credentials[3][10:-1]

	except:
		username = input("What is your username for the AVS schedule website? ")
		password = input("What is your password for the AVS schedule website? ")

		credentials_file = open("Generated Files/Credentials.txt", "w")
		credentials_file.write("This file contains your credentials for logging into the AVS schedule website\n\n")
		credentials_file.write(f"username: {username}\n")
		credentials_file.write(f"password: {password}\n")

		print("Your username and password have been saved! You can edit them at any time in the 'Credentials.txt' file located in the Generated Files folder.")

	finally:
		return username, password
