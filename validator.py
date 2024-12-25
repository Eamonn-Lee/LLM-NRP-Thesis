import os

#
def construct_command(input, validator):
    #input = "n030w4_1_6-2-9-1"

    base_dirr="INRC2_Dataset"

    instance = input.split('_')
    dataset = instance[0]
    his = instance[1]
    order = instance[2].split('-')

    sce_file=f"{base_dirr}/{dataset}/Sc-{dataset}.txt"
    his_file=f"{base_dirr}/{dataset}/H0-{dataset}-{his}.txt"

    week_files = [f"{base_dirr}/{dataset}/WD-{dataset}-{x}.txt" for x in order]

    #replace with actual solution files + path
    sol = ["INRC2_Dataset/n005w4/Solution_H_0-WD_1-2-3-3/Sol-n005w4-1-0.txt", "INRC2_Dataset/n005w4/Solution_H_0-WD_1-2-3-3/Sol-n005w4-2-1.txt", "INRC2_Dataset/n005w4/Solution_H_0-WD_1-2-3-3/Sol-n005w4-3-2.txt", "INRC2_Dataset/n005w4/Solution_H_0-WD_1-2-3-3/Sol-n005w4-3-3.txt"]

    #check instance files valid
    data_files = [sce_file, his_file] + week_files + sol
    missing = [path for path in data_files if not os.path.exists(path)]
    if missing:
        missing_files_str = "\n".join(missing)
        raise FileNotFoundError(f"The following file paths do not exist:\n{missing_files_str}")

    validate_comm = f"java -jar {validator} --sce {sce_file} --his {his_file} --weeks {' '.join(week_files)} --sols {' '.join(sol)}"
    return validate_comm