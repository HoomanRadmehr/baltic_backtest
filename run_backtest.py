from gather_data import resample_timeframe
from dataframe_creator import create_compelete_excel,get_results

starting_leverage = 5
ending_leverage = 101

starting_time_frame = 1
ending_time_frame = 49


for i in range(starting_leverage,ending_leverage):
    for y in range(starting_time_frame,ending_time_frame):
        resample_timeframe(y)
        create_compelete_excel(i,y)

get_results()
