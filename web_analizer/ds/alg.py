import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

def full_tab(df):
  df = df.replace( r'^\s\*$' , np.nan , regex= True )
  df=df.dropna()
  df=df.reset_index(drop=True)
  return df

def sum_data(t,data):
  summ=0
  for i in range(t):
      summ+=int(data[i])
  return summ

def T_finder(t,data_t,data):
  for tau in range(len(data)):
    if data_t[tau]>=data[t] or tau>=t:
      return tau

def pers_next(df_bonus):
  # fit model
  modelB = ARIMA(df_bonus['rBt'], order=(5,1,0))
  modelB_fit = modelB.fit()
  outputB = modelB_fit.forecast()
  #summary of fit model
  # print(modelB_fit.summary())


  # fit model
  modelDNM = ARIMA(df_bonus['rDNMt'], order=(5,1,0))
  modelDNM_fit = modelDNM.fit()
  outputDNM = modelDNM_fit.forecast()
  #summary of fit model
  # print(modelDNM_fit.summary())
  # print(outputB, outputDNM)
  return [outputB, outputDNM]

def get_next(n0,prevB, persB, prevDNM, persDNM):
  nextBt=(1+persB/100)*prevB
  nextDNMt=(1+persDNM/100)*prevDNM
  nt=n0+nextBt-nextDNMt
  return [nextBt, nextDNMt, nt]


def get_pred(df_bonus,years):
  df_bonus = full_tab(df_bonus)
  df_bonus = df_bonus.assign(DNM= lambda x: (x['D(t)']) + x['NM(t)'])

  print(df_bonus)

  Intb_sum=[sum_data(i+1, df_bonus['B(t)']) for i in range(len(df_bonus['B(t)']))]
  df_bonus = df_bonus.assign(IntB= Intb_sum)

  IntDNM_sum=[sum_data(i+1, df_bonus['DNM']) for i in range(len(df_bonus['DNM']))]
  df_bonus = df_bonus.assign(IntDNM= IntDNM_sum)

  rBt_t=[0]+[100*(df_bonus['IntB'][i] - df_bonus['IntB'][i-1])/df_bonus['IntB'][i] for i in range(1,len(df_bonus['IntB']))]
  df_bonus = df_bonus.assign(rBt= rBt_t)

  rDNMt_t=[0]+[100*(df_bonus['IntDNM'][i] - df_bonus['IntDNM'][i-1])/df_bonus['IntDNM'][i] for i in range(1,len(df_bonus['IntDNM']))]
  df_bonus = df_bonus.assign(rDNMt= rDNMt_t)

  tau=[0]+[i-T_finder(i,df_bonus['IntB'],df_bonus['IntDNM']) for i in range(1,len(df_bonus['IntDNM']))]
  df_bonus = df_bonus.assign(Qt= tau)

  for i in range(years):
      pers = pers_next(df_bonus)
      new_row_list = get_next(df_bonus['N(t)'][0], df_bonus['IntB'][len(df_bonus['IntB'])-1], pers[0], df_bonus['IntDNM'][len(df_bonus['IntDNM'])-1], pers[1])
      new_row_dict = {
          'Year': df_bonus['Year'].iloc[-1] + 1,
          'N(t)': int(new_row_list[2]),
          'IntB': int(new_row_list[0]),
          'IntDNM': int(new_row_list[1]),
          'rBt': float(pers[0].iloc[0]),
          'rDNMt': float(pers[1].iloc[0])
      }
      new_row_df = pd.DataFrame([new_row_dict])
      df_bonus = pd.concat([df_bonus, new_row_df], ignore_index=True)

  tau = [0] + [i - T_finder(i, df_bonus['IntB'], df_bonus['IntDNM']) for i in range(1, len(df_bonus['IntDNM']))]
  df_bonus = df_bonus.assign(Qt=tau)
  return df_bonus

# df_bonus = pd.read_csv("test.csv")
# df_bonus=get_pred(df_bonus,10)
# df_bonus.to_excel("output.xlsx")