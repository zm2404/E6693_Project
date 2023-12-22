import os

if __name__ == '__main__':
    '''
    copy the files from the directory '/user/stud/fall22/zm2404/E6693/DA3' 
    to the submission directory '/user/stud/fall22/zm2404/E6693/DA3_submission'
    '''
    designs = ['blabla-da3', 'salsa20-da3']
    da3_dir = '/user/stud/fall22/zm2404/E6693/DA3/'
    submission_dir = '/user/stud/fall22/zm2404/E6693/DA3_submission/'

    for design in designs:
        for i in range(12):
            directory = f'{design}_{i}.test'
            os.makedirs(f'{directory}')
            os.chdir(f'./{directory}')
            os.system(f'cp {da3_dir}{directory}/annotation.txt {submission_dir}{directory}')
            os.system(f'cp {da3_dir}{directory}/output.txt {submission_dir}{directory}')
            os.system(f'cp -r {da3_dir}{directory}/metrics {submission_dir}{directory}')
            os.makedirs('input')
            os.chdir('./input')
            os.system(f'cp -r {da3_dir}{directory}/input/plugs {submission_dir}{directory}/input')
            os.chdir(f'{submission_dir}')

