import os

if __name__ == '__main__':
    total_time = 0
    for i in range(30):
        os.chdir(f'DA1_{i}/reports')
        with open ('final.rpt', 'r') as file:
            for line in file:
                if 'Total Runtime' in line:
                    words = line.split(':')
                    hour = int(words[-3])
                    minute = int(words[-2])
                    second = int(words[-1])
                    total_time += hour*3600 + minute*60 + second
        
        os.chdir('../..')
    
    print('total time: ', total_time)
