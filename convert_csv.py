import os

# read additional EMG data
folder_groups = ["P1", "P2", "P3"]
folder_subgroups = ["S1", "S2", "S3"]

for folder in folder_groups:
    for subfolder in folder_subgroups:
        path = f"additional_signals/{folder}/{subfolder}"
        for file_name in os.listdir(path):
            if file_name.endswith('.csv'):
                name = int(file_name.split('.')[0]) + 8
                os.system(f"sed 's/;/,/g' additional_signals/{folder}/{subfolder}/{file_name} > additional_signals/{folder}/{subfolder}/{name}.csv")