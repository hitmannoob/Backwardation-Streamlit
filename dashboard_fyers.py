import sys
import streamlit as st
import pandas as pd
import numpy as np 
from time import strftime, localtime
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fyers_apiv3 import fyersModel
import warnings
import calendar
import datetime
from datetime import date, timedelta


warnings.filterwarnings('ignore')
st.set_page_config(page_title="Welcome to my Dashboard", layout="wide")


client_id = "UR970A7JV8-100"
secret_key = "EGBZEADBM1"
redirect_uri = "https://myapi.fyers.in/dashboard"
response_type = "code"  
state = "sample_state"
grant_type = "authorization_code" 

# session = fyersModel.SessionModel(
#     client_id=client_id,
#     secret_key=secret_key,
#     redirect_uri=redirect_uri,
#     response_type=response_type
# )

# response = session.generate_authcode()
# auth_code="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJpYXQiOjE3MzA2Mjc0MjYsImV4cCI6MTczMDY1NzQyNiwibmJmIjoxNzMwNjI2ODI2LCJhdWQiOiJbXCJ4OjBcIiwgXCJ4OjFcIiwgXCJ4OjJcIiwgXCJkOjFcIiwgXCJkOjJcIiwgXCJ4OjFcIiwgXCJ4OjBcIl0iLCJzdWIiOiJhdXRoX2NvZGUiLCJkaXNwbGF5X25hbWUiOiJZRDA4MzkzIiwib21zIjoiSzEiLCJoc21fa2V5IjoiYzFlYzMyOGNiNWI3OTgzMzZhOTE1NGUxZWE0MjIxZjQxOWExZjIwZTY3NWRmYmYyZjljZmI2MzUiLCJub25jZSI6IiIsImFwcF9pZCI6IlVSOTcwQTdKVjgiLCJ1dWlkIjoiMmExODFjYTQ1YzgwNDMyNDg3MmI1ZjVmOGQxM2M3ODgiLCJpcEFkZHIiOiIwLjAuMC4wIiwic2NvcGUiOiIifQ.EQo5ZK-cVIt8mw_rosve4-FwQbEwsX_VTiVQvcAuVHk"

# session = fyersModel.SessionModel(
#     client_id=client_id,
#     secret_key=secret_key, 
#     redirect_uri=redirect_uri, 
#     response_type=response_type, 
#     grant_type=grant_type
# )
# session.set_token(auth_code)

# response = session.generate_token()
access_token= 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3MzExMzQ1ODIsImV4cCI6MTczMTE5ODYwMiwibmJmIjoxNzMxMTM0NTgyLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbkx3UjJhTXdlam03X0VydUxqZXRkQV96SndQcVJnOUpYWGJGdFhMZjNaQTFQNnowVXVRaVRrOW5Uem9sMXh1bWtaa2lrX1ZWaDRtbHduQjlfcFRtUXl6cEM3R0RwMTJWdTFmTmVPVzZsczBMMmVxZz0iLCJkaXNwbGF5X25hbWUiOiJERUVQRVNIIFNISVZDSEFSQU4gQkFOU0FMIiwib21zIjoiSzEiLCJoc21fa2V5IjoiYzFlYzMyOGNiNWI3OTgzMzZhOTE1NGUxZWE0MjIxZjQxOWExZjIwZTY3NWRmYmYyZjljZmI2MzUiLCJmeV9pZCI6IllEMDgzOTMiLCJhcHBUeXBlIjoxMDAsInBvYV9mbGFnIjoiTiJ9.xh0Ji_LXV_67KTSMrHpCY4OBUXUQaDcwLqChuIBqQRo'
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,is_async=False, log_path="")
# st.write(fyers)

def create_graph(data_df, fut_dict):
    x=data_df['Time']
    y=data_df['Close']
    
    fig=go.Figure()
    # st.write("Reached here")

    for k, v in fut_dict.items():

        fig.add_traces(go.Scatter(x= v['Time'], y= v['Close'], mode='lines', name=k))


    # fig.add_trace(go.Scatter(x=fut_df['Time'],y=fut_df['Close']))
    fig.add_traces(go.Scatter(x=x,y=y,mode='lines', name='Underlying Price'))
    # fig.add_trace(go.Bar(x=x,y=volume, name='Volume'))

    return fig



def get_data(fyers_obj, symbol, start_date='2024-01-01', end_date= date.today()):
    start_date=end_date- timedelta(days=366)

    data = {
    "symbol":f"NSE:{symbol}-EQ",
    "resolution":"D",
    "date_format":"1",
    "range_from": start_date,
    "range_to":end_date,
    "cont_flag":"0"
    }
    response = fyers_obj.history(data=data)
    # st.write(response)
    data_df=pd.DataFrame.from_dict(response['candles'])
    data_df.rename(columns={0:"Time",1:"Open", 2:"High",3:"Low", 4:"Close",5:"Volume"}, inplace=True)
    
    for x in range(len(data_df['Time'])):
        data_df['Time'][x]=strftime('%Y-%m-%d', localtime(data_df['Time'][x]))
    
    return data_df

def get_last_thursday(year, month):

    last_day = calendar.monthrange(year, month)[1]
    last_date = datetime.date(year, month, last_day)
    last_weekday = last_date.weekday()
    days_to_go_back = (last_weekday - 3) % 7
    last_thursday = last_date - datetime.timedelta(days=days_to_go_back)

    return last_thursday



def get_expiries():
    available_expiries=[]
    cmon=date.today().month
    year=date.today().year
    available_expiries.append(get_last_thursday(year, cmon))


    count=1
    while count<3:
        if cmon+count>12:
            year=year+1
            cmon=cmon-12
            available_expiries.append(get_last_thursday(year, cmon+count))
        else:
            available_expiries.append(get_last_thursday(year, cmon+count))
        count=count+1



    return available_expiries


def calculate_future_price(fyers_obj,available_expiry_list, brand,  start_date='2024-01-01', end_date= date.today()):
    mont_mapping={1:"JAN", 2:"FEB", 3:"MAR",4:"APR", 5:"MAY", 6:"JUN", 7:"JUL",8:"AUG", 9:"SEP", 10:"OCT",11:"NOV", 12:"DEC"}

    fut_dict={}
    for e,v in available_expiry_list.items():
        # fut_dict={}
        if v:
            symbol=brand
            e=str(e)
            symbol=symbol+str(24)
            symbol=symbol+mont_mapping[int(e[5:7])]
            data = {
                "symbol":f"NSE:{symbol}FUT",
                "resolution":"D",
                "date_format":"1",
                "range_from": start_date,
                "range_to":end_date,
                "cont_flag":"0"
            }
            response = fyers_obj.history(data=data)

            fut_data_df=pd.DataFrame.from_dict(response['candles'])
            fut_data_df.rename(columns={0:"Time",1:"Open", 2:"High",3:"Low", 4:"Close",5:"Volume"}, inplace=True)
    
            for x in range(len(fut_data_df['Time'])):
                fut_data_df['Time'][x]=strftime('%Y-%m-%d', localtime(fut_data_df['Time'][x]))

            fut_dict[e]=fut_data_df


    return fut_dict





if __name__ == "__main__":
    brand_df = pd.read_csv(r"C:\Users\dshivcharanbansal\Documents\company_brand_mapping.csv")
    brand=st.sidebar.selectbox("Choose the Stock", tuple(brand_df['Company']) )
    company_brand_mapping=dict(zip(brand_df["Company"], brand_df['Symbol']))
    symbol=company_brand_mapping[brand]

    selected_expiries={}
    available_expiries=get_expiries()

    with st.sidebar.expander("Select the expiry date"):
        all_expiry=st.checkbox("All expiries", value=False)

        with st.form("Available expiries"):

            l_1=st.checkbox(str(available_expiries[0]),value= all_expiry)
            l_2=st.checkbox(str(available_expiries[1]), value= all_expiry)
            l_3=st.checkbox(str(available_expiries[2]), value=all_expiry)




            submitted = st.form_submit_button("Calculate Charts")
    if submitted:
            selected_expiries={str(available_expiries[0]):l_1, str(available_expiries[1]):l_2,str(available_expiries[2]): l_3 }
                            
            eq_data_df=get_data(fyers, symbol)
            fut_data_dict=calculate_future_price(fyers,selected_expiries, symbol )
            figure=create_graph(eq_data_df, fut_data_dict)
            st.plotly_chart(figure, use_container_width=True)










