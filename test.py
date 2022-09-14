# Python program to convert time
# from 12 hour to 24 hour format
import datetime
import pytz

timeZ_Ny = pytz.timezone('America/New_York')
UTC = pytz.utc


dt_Ny = datetime.datetime.now(timeZ_Ny)
e = dt_Ny
current_time = (e.strftime("%I:%M:%S %p"))
#function to convert date time to miliary time
m1 = current_time
m2 = datetime.datetime.strptime(m1, "%I:%M:%S %p").time()
# Function to convert the date format
def convert24(str1):
	
	# Checking if last two elements of time
	# is AM and first two elements are 12
	if str1[-2:] == "AM" and str1[:2] == "12":
		return "00" + str1[2:-2]
		
	# remove the AM	
	elif str1[-2:] == "AM":
		return str1[:-2]
	
	# Checking if last two elements of time
	# is PM and first two elements are 12
	elif str1[-2:] == "PM" and str1[:2] == "12":
		return str1[:-2]
		
	else:
		
		# add 12 to hours and remove PM
		return str(int(str1[:2]) + 12) + str1[2:8]

# Driver Code		
current_military_time = (convert24(current_time)) 
print(current_military_time)