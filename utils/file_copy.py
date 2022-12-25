import shutil
import os

base_path = "../BinRushed1-Corrected"
copy_path = os.path.join(base_path, "Copied")
if not os.path.exists(copy_path):
    os.mkdir(copy_path)

for k in range(1, 25):
    for i in range(1, 7):
        if i == 3:
            continue
        new_file = "image" + str(k) + "-" + str(i) + ".jpg"
        dst = os.path.join(copy_path, new_file)
        shutil.copy(os.path.join(base_path, "image" + str(k) + "prime.jpg"), dst)


