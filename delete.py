from datetime import *
import pytz
timeZ_Ny = pytz.timezone('America/New_York')
UTC = pytz.utc
import datetime

dt_Ny = datetime.datetime.now(timeZ_Ny)
e = dt_Ny
current_time = (e.strftime("%I:%M:%S %p"))
m1 = current_time

m2 = datetime.datetime.strptime(m1, "%I:%M:%S %p").time()
print(m2)

# import datetime

# today = '2022-09-14 12:07:15.509448'#datetime.datetime.now()
# print(today)
# date_time = today.strftime("%H:%M:%S")
# print("date and time:",date_time)

