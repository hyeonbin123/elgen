from glob import glob
import shutil
import os


filepath1 = '/home/elgen/devOps/Recording/data/2022/*/*'
filepath2 = '/home/elgen/devOps/Recording/data/2022/*/*/local_upload'
filepath3 = '/home/elgen/devOps/Recording/data/2022/*/*/split/*'
filepath4 = '/home/elgen/devOps/Recording/data/2022/*/*/local_upload/split/*'

filepath5 = '/data/traindata/2022/*/*/*/m3u8'
filepath6 = 'C:/data/traindata/2022/*/*/*/m3u8'
total_list2 = glob(filepath5)
#print(total_list2)

for total2 in total_list2:
    if os.path.isdir(total2):
        print(total2)
        shutil.rmtree(total2)
        print('삭제완료!!!')

'''
total_list = glob(filepath4 + "/*.txt")
print(total_list)

for total in total_list:
    with open(total, 'r', encoding='UTF8') as file:
        lines = file.readlines()

    with open(total, "w", encoding='UTF8') as f:
        for line in lines:
            if '류머티즘' in line:
                print('류머티즘 있음')
                print(total)
            if '류머티스' in line:
                print('류머티스 있음')
                print(total)
            
            if '류마티스' in line:
                print('류마티스 있음')
                print(total)

            line = line.replace('류머티즘', '류마티스')
            line = line.replace('류머티스', '류마티스')
            f.write(line)
            if '류머티즘' in line:
                print('류머티즘이 없어야하는데 있네..')
            if '류머티스' in line:
                print('류머티스가 없어야하는데 있네..')
'''



