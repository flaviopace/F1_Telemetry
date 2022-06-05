import fastf1 as ff1
from fastf1 import plotting
from fastf1 import utils
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema
import numpy as np
import pandas as pd

ff1.Cache.enable_cache('/tmp/fastf1')  # replace with your cache directory
ff1.plotting.setup_mpl()

year = 2021
race = 'Monaco'
session = 'FP2'
d1 = 'LEC'
d2 = 'HAM'

quali = ff1.get_session(int(year), race, session)
laps = quali.load_laps(with_telemetry=True)

d1_lap = laps.pick_driver(d1).pick_fastest()
d2_lap = laps.pick_driver(d2).pick_fastest()

d1_lap_time = d1_lap['LapTime'].total_seconds()
d2_lap_time = d2_lap['LapTime'].total_seconds()
m1, s1 = divmod(d1_lap_time, 60)
m2, s2 = divmod(d2_lap_time, 60)
s1 = '%06.3f' % s1
s2 = '%06.3f' % s2

delta_time, ref_tel, compare_tel = utils.delta_time(d1_lap, d2_lap)

#Plotting max and min relative speeds

df1 = pd.DataFrame(ref_tel, columns=['Speed'])
df2 = pd.DataFrame(compare_tel, columns=['Speed'])

#argrelextrema non funziona con dati rumorosi

df1 = df1.interpolate()
df2 = df2.interpolate()

n = 10

df1['min'] = df1.iloc[argrelextrema(df1.Speed.values, np.less_equal, order=n)[0]]['Speed']
df1['max'] = df1.iloc[argrelextrema(df1.Speed.values, np.greater_equal, order=n)[0]]['Speed']

df2['min'] = df2.iloc[argrelextrema(df2.Speed.values, np.less_equal, order=n)[0]]['Speed']
df2['max'] = df2.iloc[argrelextrema(df2.Speed.values, np.greater_equal, order=n)[0]]['Speed']

#droppo i dati che si ripetono
df1_list= df1['max'].to_list()
df2_list= df2['max'].to_list()

#primo dataframe range di un intorno di 2 valori con 'buco'
#vel max

#This code is used to keep only 1 value within the interval of max 4 repetition
for i in df1.index:
    if 0 <= i-4 < len(df1_list):
        if df1['max'][i] == df1['max'][i-4]:
            df1['max'][i-4] = np.nan

for i in df1.index:
    if 0 <= i-3 < len(df1_list):
        if df1['max'][i] == df1['max'][i-3]:
            df1['max'][i-3] = np.nan

for i in df1.index:
    if 0 <= i-2 < len(df1_list):
        if df1['max'][i] == df1['max'][i-2]:
            df1['max'][i-2] = np.nan

for i in df1.index:
    if 0 <= i-1 < len(df1_list):
        if df1['max'][i] == df1['max'][i-1]:
            df1['max'][i-1] = np.nan

#vel min

for i in df1.index:
    if 0 <= i-4 < len(df1_list):
        if df1['min'][i] == df1['min'][i-4]:
            df1['min'][i-4] = np.nan

for i in df1.index:
    if 0 <= i-3 < len(df1_list):
        if df1['min'][i] == df1['min'][i-3]:
            df1['min'][i-3] = np.nan

for i in df1.index:
    if 0 <= i-2 < len(df1_list):
        if df1['min'][i] == df1['min'][i-2]:
            df1['min'][i-2] = np.nan

for i in df1.index:
    if 0 <= i-1 < len(df1_list):
        if df1['min'][i] == df1['min'][i-1]:
            df1['min'][i-1] = np.nan

#secondo dataframe range di un intorno di 2 valori con 'buco'
#vel max
for i in df2.index:
    if 0 <= i-4 < len(df2_list):
        if df2['max'][i] == df2['max'][i-4]:
            df2['max'][i-4] = np.nan

for i in df2.index:
    if 0 <= i-3 < len(df2_list):
        if df2['max'][i] == df2['max'][i-3]:
            df2['max'][i-3] = np.nan

for i in df2.index:
    if 0 <= i-2 < len(df2_list):
        if df2['max'][i] == df2['max'][i-2]:
            df2['max'][i-2] = np.nan

for i in df2.index:
    if 0 <= i-1 < len(df2_list):
        if df2['max'][i] == df2['max'][i-1]:
            df2['max'][i-1] = np.nan

#vel min

for i in df2.index:
    if 0 <= i-4 < len(df1_list):
        if df2['min'][i] == df2['min'][i-4]:
            df2['min'][i-4] = np.nan

for i in df2.index:
    if 0 <= i-3 < len(df1_list):
        if df2['min'][i] == df2['min'][i-3]:
            df2['min'][i-3] = np.nan

for i in df2.index:
    if 0 <= i-2 < len(df1_list):
        if df2['min'][i] == df2['min'][i-2]:
            df2['min'][i-2] = np.nan

for i in df2.index:
    if 0 <= i-1 < len(df1_list):
        if df2['min'][i] == df2['min'][i-1]:
            df2['min'][i-1] = np.nan

plt.ioff()
fig, ax = plt.subplots(1)

ax.plot(ref_tel['Distance'], ref_tel['Speed'],
color='red', label=d1)
ax.plot(compare_tel['Distance'], compare_tel['Speed'],
color='green', label=d2)

plt.scatter(ref_tel['Distance'], df1['min'], c='r')
plt.scatter(ref_tel['Distance'], df1['max'], c='r')
plt.scatter(compare_tel['Distance'], df2['min'], c='g')
plt.scatter(compare_tel['Distance'], df2['max'], c='g')

ax.set_xlabel('Distance in m')
ax.set_ylabel('Speed in km/h')

plt.suptitle(f"Fastest Lap Comparison \n "
f"{quali.weekend.name} {quali.weekend.year} Qualifying \n"
f"{d1}={int(m1)}.{s1} {d2}={int(m2)}.{s2}")

twin = ax.twinx()
twin.plot(ref_tel['Distance'], delta_time, '--', color='white', alpha=0.25)
twin.set_ylabel(f"<-- {d2} ahead | {d1} ahead -->")

#Prima di annotare i punti li trasformo in numpy 1d array
df1_list_max = df1['max'].to_numpy()
df1_list_min = df1['min'].to_numpy()
df2_list_max = df2['max'].to_numpy()
df2_list_min = df2['min'].to_numpy()
distance_list_ref = ref_tel['Distance'].to_numpy()
distance_list_com = compare_tel['Distance'].to_numpy()

for x, y in zip(distance_list_ref, df1_list_max):
    label = "{:.2f}".format(y)
    ax.annotate(label, # this is the text
    (x, y), # these are the coordinates to position the label
    textcoords="offset points", # how to position the text
    xytext=(-23, 10), # distance from text to points (x,y)
    ha='center', # horizontal alignment can be left, right or center
    color='red') # setting the color of the annotation
for x, y in zip(distance_list_ref, df1_list_min):
    label = "{:.2f}".format(y)
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(-23, -10), ha='center', color='red')

for x, y in zip(distance_list_com, df2_list_max):
    label = "{:.2f}".format(y)
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(23, 10), ha='center', color='green')

for x, y in zip(distance_list_com, df2_list_min):
    label = "{:.2f}".format(y)
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(23, -10), ha='center', color='green')

#Inserisco il tempo sul giro dei piloti

ax.legend(loc = 'lower left', bbox_to_anchor = (0,1.02,1,0.2),
fancybox = True, shadow = True, ncol = 5)

plt.show()