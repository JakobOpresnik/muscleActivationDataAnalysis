import os
import matplotlib.pyplot as plt
import myo
import time
import csv
import math
from enum import Enum

# initialize Myo
myo.init(sdk_path="G:\\Other computers\\Home Desktop\\Google Drive\\FERI\\MAGISTERIJ\\2. semester\\Nevro, Nano in Kvantno Racunalnistvo\\vaje\\vaja1\\sdk\\myo-sdk-win-0.9.0")

duration = 35
sampling_rate = 200  # Hz

class Graph(Enum):
    RMS = 1
    ARV = 2

# custom Myo listener to collect EMG data and plot it live
class EmgPlotter(myo.DeviceListener):
    def __init__(self, num_sensors, max_rows, window_size, figure, axes, graph_selection):
        #super().__init__()
        self.num_sensors = num_sensors
        self.emg_data = [[] for _ in range(num_sensors)]
        self.plotting = True
        self.start_time = time.time()
        self.rows_written = 0
        self.max_rows = max_rows
        self.window_size = window_size
        self.fig = figure
        self.ax = axes
        self.graph_selection = graph_selection
        self.rms_data = [[] for _ in range(num_sensors)]
        self.arv_data = [[] for _ in range(num_sensors)]
        
    def on_connected(self, event):
        print("Myo connected")
        event.device.stream_emg(True)  # enable streaming of EMG data
    
    def on_disconnected(self, event):
        print("Myo disconnected")

    def on_emg(self, event):
        # Adjust the width ratios
        emg_data = event.emg
        for i in range(self.num_sensors):
            self.emg_data[i].append(emg_data[i])
        if self.plotting:
            self.plot_live(fig, ax)
            self.rows_written += 1
            if self.rows_written >= self.max_rows:
                self.plotting = False
                self.print_countdown()
    
    def print_countdown(self):
        # print countdown timer
        if self.plotting:
            remaining_time = self.start_time + duration - time.time()
            print(f"Time remaining: {remaining_time:.2f} seconds", end="\r")
            if remaining_time <= 0:
                print("\nTime's up!")
                self.plotting = False
    
    def plot_live(self, fig, ax, replay=False, file_name=None):
        fig.suptitle(f"8 muscle activation Myo armband sensors {f'({file_name})' if file_name is not None else ''}", fontsize=18, y=0.96)
        fig.subplots_adjust(hspace=0.5, wspace=0.1, top=0.85)

        n = 15  # for calculating RMS & ARV
        
        for i in range(self.num_sensors):

            ax[0, 0].set_title("EMG data", fontsize=15)
            ax[0, 1].set_title("RMS data" if self.graph_selection == Graph.RMS.value else "AVR data", fontsize=15)

            # EMG plots
            ax[i, 0].clear()

            start = len(self.emg_data[i]) - self.window_size
            end = min(len(self.emg_data[i]), start + 200)
            x = range(end, abs(start)+(end*2)) if start <= 0 else range(start, end)
            y = [0]*abs(start) + self.emg_data[i][0:end] if start <= 0 else self.emg_data[i][start:start+end]

            ax[i, 0].plot(x, y)
            
            ax[i, 0].set_xticks([])
            ax[i, 0].set_yticks([])

            ax[i, 0].set_ylim([-128, 128])

            if i == 7:
                ax[i, 0].set_xlabel("elapsed time" if not replay else "rows read", labelpad=15, fontsize=12)

            if i == 4: ax[i, 0].set_ylabel("EMG values", labelpad=15, fontsize=12)

            match self.graph_selection:
                case Graph.RMS.value:
                    # RMS plots
                    ax[i, 1].clear()

                    ax[i, 1].set_xticks([])
                    ax[i, 1].set_yticks([])

                    ax[i, 1].set_ylim([0, 128])

                    # calculate RMS
                    self.rms_data[i].append(math.sqrt(1/end*sum([j**2 for j in self.emg_data[i][0:end]])) if end <= n else math.sqrt(1/n*sum(([j**2 for j in self.emg_data[i][end-n:end]]))))
                    z = [0]*abs(start) + self.rms_data[i] if start <= 0 else self.rms_data[i][start:start+end]

                    ax[i, 1].plot(x, z)
                
                case Graph.ARV.value:
                    # ARV plots
                    ax[i, 1].clear()

                    ax[i, 1].set_xticks([])
                    ax[i, 1].set_yticks([])

                    ax[i, 1].set_ylim([0, 128])

                    # calculate ARV
                    self.arv_data[i].append(1/end*sum([abs(j) for j in self.emg_data[i][0:end]]) if end <= n else 1/n*sum(([abs(j) for j in self.emg_data[i][end-n:end]])))
                    z = [0]*abs(start) + self.arv_data[i] if start <= 0 else self.arv_data[i][start:start+end]

                    ax[i, 1].plot(x, z)
                
                case '':
                    print("\nERROR: no input provided!")
                
                case _:
                    print("\nERROR: incorrect input!")
            
            if not replay: self.print_countdown()

        plt.pause(1 / 200)  # pause to allow the plot to update

# save EMG data to .csv file
def save_data(file_path):
    print(f"saving EMG data to {file_path}...")
    # crop out first and last 2.5 seconds of data
    start_index = int(2.5 * sampling_rate)
    end_index = int((duration - 2.5) * sampling_rate)
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([f"sensor {i+1}" for i in range(NUM_SENSORS)])  # write header
        for i in range(start_index, end_index):
            # if less data has been retrieved than it is required, then zeros are added to the end
            if len(plotter.emg_data[0]) <= i:
                writer.writerow([0 for _ in range(NUM_SENSORS)])
            else:
                writer.writerow([plotter.emg_data[j][i] for j in range(NUM_SENSORS)])  # write data row by row
    print(f"EMG data saved to {file_path}")

# return existing .csv files inside this directory & all subdirectories
def check_csv_files():
    csv_files = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

# load EMG data from .csv file
def load_data(file_path):
    emg_data = [[] for _ in range(NUM_SENSORS)]
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip first (header) row
        for row in reader:
            for i in range(NUM_SENSORS):
                emg_data[i].append(float(row[i]))
    return emg_data

# plot loaded data again
def replay_data(emg_data, file_name, fig, ax):
    num_samples = len(emg_data[0])

    for i in range(0, num_samples+1):
        for j in range(NUM_SENSORS):
            plotter.emg_data[j] = emg_data[j][:i+1]

        plotter.plot_live(fig, ax, replay=True, file_name=file_name)

        time.sleep(1/200)

def menu():
    print('''
=====================================
What would you like to do?
=====================================
1...RECORD LIVE & SAVE DATA TO FILE
2...LOAD DATA FROM FILE
3...EXIT
''')
    selection = input("Enter your choice: ")
    return selection

def submenu():
    print('''
====================================================
Which graph would you like to see for the EMG data          
====================================================
1...RMS (Root Mean Square)
2...ARV (Average Rectified Value)
''')


if __name__ == '__main__':
    running = True
    fig, ax = plt.subplots(8, 2)

    while running:
        selection = menu()
        submenu()
        graph_selection = int(input("Enter your choice: "))
        print(graph_selection)
        print(Graph.RMS.value)
        match selection:
            case '1':
                # the 8 hand movements we'll be recording
                movements = ["fist", "extension", "flexion", "ulnar_deviation", "radial_deviation", "pronation", "supination", "neutral"]

                # create .csv file names for all 8 hand movements
                csv_files = [mov + ".csv" for mov in movements]

                # execute script for each of the hand movements
                for movement, file_name in zip(movements, csv_files):
                    # create an instance of the EmgPlotter with desired parameters
                    NUM_SENSORS = 8
                    max_rows = duration * sampling_rate
                    plotter = EmgPlotter(num_sensors=NUM_SENSORS, max_rows=max_rows, window_size=200, figure=fig, axes=ax, graph_selection=graph_selection)

                    print(f"\nCurrent movement: {movement}")

                    # start collecting EMG data in the background indefinitely
                    hub = myo.Hub()
                    hub.run(plotter, duration*1000)  # time in ms
                    
                    # save data to file
                    save_data(file_name)

                    # pause for 5 seconds                
                    time.sleep(5)
                
            case '2':
                csv_files = check_csv_files()
                if csv_files:
                    print("\nAVAILABLE CSV FILES:")
                    numbers = [i for i in range(1, len(csv_files)+1)]
                    file_dict = {}
                    for number, file in zip(numbers, csv_files):
                        print(f"{number}..{file}")
                        file_dict[number] = file
                    file_num = int(input("\nEnter number which corresponds to the file you would like to load and replay: "))
                    file_name = file_dict[file_num]
                    print(f"replaying data from {file_name}...")
                    NUM_SENSORS = 8
                    emg_data = load_data(file_name)
                    if emg_data:
                        # create an instance of the EmgPlotter with desired parameters
                        max_rows = duration * sampling_rate
                        plotter = EmgPlotter(num_sensors=NUM_SENSORS, max_rows=max_rows, window_size=200, figure=fig, axes=ax, graph_selection=graph_selection)
                        replay_data(emg_data, file_name, fig, ax)
                    else:
                        print("Error loading data from file.")
                else:
                    print("\nNo .csv files with EMG data available yet!")

            case '3':
                running = False

            case '':
                print("\nERROR: no input provided!")
            
            case _:
                print("\nERROR: incorrect input!")