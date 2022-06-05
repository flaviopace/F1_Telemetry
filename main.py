import matplotlib.pyplot as plt
import fastf1.plotting
import numpy as np

fastf1.Cache.enable_cache('/tmp/fastf1')  # replace with your cache directory

# we only want support for timedelta plotting in this example
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None, misc_mpl_mods=False)

session = fastf1.get_session(2022, 'Imola', 'Q')
session.load()

# Get the laps
laps = session.load_laps(with_telemetry=True)

lec_fast = laps.pick_driver('LEC').pick_fastest()
ver_fast = laps.pick_driver('VER').pick_fastest()

# Get telemetry from fastest laps
lec_telemetry = lec_fast.get_car_data().add_distance()
ver_telemetry = ver_fast.get_car_data().add_distance()

tel_data = ["Speed", "Throttle", "Brake", "nGear", "RPM", "DRS"]

# Create plot
fig, ax = plt.subplots(len(tel_data) + 1)
fig.suptitle("Fastest Race Lap Telemetry Comparison")

lec_color = fastf1.plotting.team_color('Ferrari')
ver_color = fastf1.plotting.team_color('Red Bull')

# Create Delta time
delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(lec_fast, ver_fast)

plot_size = [15, 15]
plot_title = f"LEC VS VER"
plot_ratios = [1, 3, 2, 1, 1, 2, 1]

# Delta line
ax[0].plot(ref_tel['Distance'], delta_time, color=lec_color)
ax[0].axhline(0)
ax[0].set(ylabel=f"Gap to")

for idx in range(len(tel_data)):
    ax[idx + 1].plot(lec_telemetry['Distance'], lec_telemetry[tel_data[idx]], label='LEC', color=lec_color)
    ax[idx + 1].plot(ver_telemetry['Distance'], ver_telemetry[tel_data[idx]], label='VER', color=ver_color)
    ax[idx + 1].set(ylabel=tel_data[idx])
    ax[idx + 1].legend(loc="lower right")

# Hide x labels and tick labels for top plots and y ticks for right plots.
for a in ax.flat:
    a.label_outer()

plt.show()

# Compute Amazon Corner telemetry

distance_min = 500
distance_max = 1000

# Assigning labels to what the drivers are currently doing
lec_telemetry.loc[lec_telemetry['Brake'] > 0, 'CurrentAction'] = 'Brake'
lec_telemetry.loc[lec_telemetry['Throttle'] > 98, 'CurrentAction'] = 'Full Throttle'
lec_telemetry.loc[(lec_telemetry['Brake'] == 0) & (lec_telemetry['Throttle'] < 98), 'CurrentAction'] = 'Cornering'

ver_telemetry.loc[ver_telemetry['Brake'] > 0, 'CurrentAction'] = 'Brake'
ver_telemetry.loc[ver_telemetry['Throttle'] > 98, 'CurrentAction'] = 'Full Throttle'
ver_telemetry.loc[(ver_telemetry['Brake'] == 0) & (ver_telemetry['Throttle'] < 98), 'CurrentAction'] = 'Cornering'

# Numbering each unique action to identify changes, so that we can group later on
lec_telemetry['ActionID'] = (lec_telemetry['CurrentAction'] != lec_telemetry['CurrentAction'].shift(1)).cumsum()
ver_telemetry['ActionID'] = (ver_telemetry['CurrentAction'] != ver_telemetry['CurrentAction'].shift(1)).cumsum()

# Identifying all unique actions
lec_actions = lec_telemetry[['ActionID', 'CurrentAction', 'Distance']].groupby(['ActionID', 'CurrentAction']).max('Distance').reset_index()
ver_actions = ver_telemetry[['ActionID', 'CurrentAction', 'Distance']].groupby(['ActionID', 'CurrentAction']).max('Distance').reset_index()

lec_actions['Driver'] = 'LEC'
ver_actions['Driver'] = 'VER'

# Calculating the distance between each action, so that we know how long the bar should be
lec_actions['DistanceDelta'] = lec_actions['Distance'] - lec_actions['Distance'].shift(1)
lec_actions.loc[0, 'DistanceDelta'] = lec_actions.loc[0, 'Distance']

ver_actions['DistanceDelta'] = ver_actions['Distance'] - ver_actions['Distance'].shift(1)
ver_actions.loc[0, 'DistanceDelta'] = ver_actions.loc[0, 'Distance']

# Merging together
all_actions = lec_actions.append(ver_actions)

# Calculating average speed
avg_speed_driver_1 = np.mean(lec_telemetry['Speed'].loc[
    (lec_telemetry['Distance'] >= distance_min) &
        (lec_telemetry['Distance'] >= distance_max)
])


avg_speed_driver_2 = np.mean(ver_telemetry['Speed'].loc[
    (ver_telemetry['Distance'] >= distance_min) &
        (ver_telemetry['Distance'] >= distance_max)
])

if avg_speed_driver_1 > avg_speed_driver_2:
    speed_text = f"{lec_fast['Driver']} {round(avg_speed_driver_1 - avg_speed_driver_2,2)}km/h faster than {ver_fast['Driver']}"
else:
    speed_text = f"{ver_fast['Driver']} {round(avg_speed_driver_2 - avg_speed_driver_1,2)}km/h faster than {lec_fast['Driver']}"

##############################
#
# Setting everything up
#
##############################
plt.rcParams["figure.figsize"] = [13, 4]
plt.rcParams["figure.autolayout"] = True

telemetry_colors = {
    'Full Throttle': 'green',
    'Cornering': 'grey',
    'Brake': 'red',
}

fig, ax = plt.subplots(3)

##############################
#
# Lineplot for speed
#
##############################
ax[0].plot(lec_telemetry['Distance'], lec_telemetry['Speed'], label=lec_actions['Driver'],
           color=fastf1.plotting.team_color('Ferrari'))
ax[0].plot(ver_telemetry['Distance'], ver_telemetry['Speed'], label=ver_actions['Driver'],
           color=fastf1.plotting.team_color('Red Bull'))

# Speed difference
ax[0].text(distance_min + 15, 200, speed_text, fontsize=15)

ax[0].set(ylabel='Speed')
#ax[0].legend((line1, line2), ('LEC', 'VER'), loc="lower right")

##############################
#
# Lineplot for Gear
#
##############################
ax[2].plot(lec_telemetry['Distance'], lec_telemetry['nGear'], label=lec_actions['Driver'],
           color=fastf1.plotting.team_color('Ferrari'))
ax[2].plot(ver_telemetry['Distance'], ver_telemetry['nGear'], label=ver_actions['Driver'],
           color=fastf1.plotting.team_color('Red Bull'))

# Speed difference
#ax[2].text('Gear', fontsize=15)

ax[2].set(ylabel='Gear')

##############################
#
# Horizontal barplot for telemetry
#
##############################
for driver in [lec_fast['Driver'], ver_fast['Driver']]:
    driver_actions = all_actions.loc[all_actions['Driver'] == driver]

    previous_action_end = 0
    for _, action in driver_actions.iterrows():
        ax[1].barh(
            action['Driver'],
            action['DistanceDelta'],
            left=previous_action_end,
            color=telemetry_colors[action['CurrentAction']]
        )

        previous_action_end = previous_action_end + action['DistanceDelta']

##############################
#
# Styling of the plot
#
##############################
# Set x-label
plt.xlabel('Distance')

# Invert y-axis
plt.gca().invert_yaxis()

# Remove frame from plot
ax[1].spines['top'].set_visible(False)
ax[1].spines['right'].set_visible(False)
ax[1].spines['left'].set_visible(False)

# Add legend
labels = list(telemetry_colors.keys())
handles = [plt.Rectangle((0, 0), 1, 1, color=telemetry_colors[label]) for label in labels]
ax[1].legend(handles, labels)

# Zoom in on the specific part we want to see
ax[0].set_xlim(distance_min, distance_max)
ax[1].set_xlim(distance_min, distance_max)
ax[2].set_xlim(distance_min, distance_max)

# Save the plot
plt.show()
