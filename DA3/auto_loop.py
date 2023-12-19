'''
Author: Matthew Ziegler (mz2976@columbia.edu)
Date: Fall 2023 - EECS 6693
Description: Example for cloning cu-adam-flow & switching submodule branches
'''
import os
import subprocess
import paramiko
import time

def system_echo(command=None):
    print(command)
    return os.system(command)


def clone_and_modify_repo(design, trial_index, syn_dp_aoe, syn_dp_area, syn_incr_opt, pnr_dfe_ext):
    #################### Add ssh key ####################
    os.system('ssh-add ~/.ssh/zm2404_key')
    os.chdir('/user/stud/fall22/zm2404/E6693/DA3')

    flow_branch  = 'adam-flow-da3'
    trial_rundir = './'+design+'_'+str(trial_index)+'.test'

    ############ clone cu-adam-flow to a local run dir ############
    system_echo('git clone --single-branch --branch '+flow_branch+' git@github.com:mmziegle/cu-adam-flow.git '+trial_rundir)
    os.chdir(trial_rundir)
    
    # record the annotation
    with open('annotation.txt', 'w') as f:
        f.write('syn_dp_aoe: '+str(syn_dp_aoe))
        f.write(' syn_dp_area: '+str(syn_dp_area))
        f.write(' syn_incr_opt: '+str(syn_incr_opt))
        f.write(' pnr_dfe_ext: '+str(pnr_dfe_ext))

    # initialize the submodule
    system_echo('git submodule update --init --recursive --remote')

    # checkout a submodule branch, i.e., switch to a specific design
    os.chdir('./input')
    system_echo('git checkout design-'+design)
    os.chdir('./plugs')
    
    ############### create <design>.elab_post.tcl ###############
    if any([syn_dp_aoe, syn_dp_area, syn_incr_opt]):
        os.makedirs("genus", exist_ok=True)         # create genus dir
        os.chdir('./genus')                         # enter genus dir
        with open(design[:-4]+'.elab_post.tcl', 'w') as f:
            if syn_dp_aoe:
                f.write('set_db dp_analytical_opt extreme\n')
            if syn_dp_area:
                f.write('set_db dp_analytical_opt off\nset_db dp_area_mode true\n')
            if syn_incr_opt:
                f.write('set gn::SYN_INCR true\n')
    os.chdir('..')                              # exit genus dir

    ############# create <design>.floorplan_post.tcl #############
    if pnr_dfe_ext:
        os.makedirs("innovus", exist_ok=True)       # create innovus dir
        os.chdir('./innovus')                       # enter innovus dir
        with open(design[:-4]+'.floorplan_post.tcl', 'w') as f:
            f.write('set_db design_flow_effort extreme\n')
    os.chdir('..')                              # exit innovus dir


def get_load(username, password, target) -> dict:
    '''
    This function is to get the load of the [target] server.
    It uses the paramiko library to ssh into the server and run the command 'top'.

    The output is a dictionary with two keys: 'load' and 'cpu'.
    '''

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's key
    ssh_client.connect(target, username=username, password=password)

    stdin, stdout, stderr = ssh_client.exec_command('top -n 1 -b')	# change the command
    output = stdout.read().decode()

    load_output = []
    lines = output.split('\n')
    for i in range(len(lines)):
        if 'load average' in lines[i]:
            load_output.append(lines[i])
            load_info = lines[i].split('load average: ')[1].split(',')

    ssh_client.close()

    return load_info


def multiple_load(username, password) -> dict:
    '''
    This function is to get the load of all the servers.
    It calls the get_load function in loop.
    '''
    # we have 42 servers
    info = {}
    for i in range(1,43):
        try:
            if i < 10:
                target = 'cadpc0' + str(i) + '.ee.columbia.edu'
            else:
                target = 'cadpc' + str(i) + '.ee.columbia.edu'
            info[i] = get_load(username, password, target)
            print('Done with ' + target)
        except:
            print('Error with ' + target)

    return info


def load_deter(username, password, des_len=12) -> list:
    '''
    This function will collect the load of all the servers, and determine which server to use.
    It will return a list of server ranked in order of idleness
    '''
    info = multiple_load(username, password)    # get the load of all the servers

    # sort the servers by their load
    sorted_info = sorted(info.items(), key=lambda x: x[1])
    ranked_servers = [x[0] for x in sorted_info]
    servers = []
    for server in ranked_servers:
        if server < 10:
            servers.append('cadpc0'+str(server)+'.ee.columbia.edu')
        else:
            servers.append('cadpc'+str(server)+'.ee.columbia.edu')

    return servers[:des_len]



if __name__ == '__main__':
    syn_dp_aoe = [0, 1]
    syn_dp_area = [0, 1]
    syn_incr_opt = [0, 1]
    pnr_dfe_ext = [0, 1]
    designs = ['blabla-da3', 'salsa20-da3']

    username = 'zm2404'
    password = '1111111'
    filedir = '/user/stud/fall22/zm2404/E6693/DA3/'


    ################# Clone and modify repo #################
    for design in designs:
        trial_index = 0
        for aoe in syn_dp_aoe:
            for area in syn_dp_area:
                for opt in syn_incr_opt:
                    for ext in pnr_dfe_ext:
                        if aoe == 1 and area == 1:
                            continue
                        clone_and_modify_repo(design, trial_index, aoe, area, opt, ext)    # clone git
                        trial_index += 1

    total_trials_num = trial_index*2
    ################# Run trials #################
    done_trials_num = 0

    while done_trials_num < total_trials_num:
        # get the available servers
        available_servers = load_deter(username, password, des_len=24)      # get the available servers
        print(available_servers)

        trial_len = min(len(available_servers), total_trials_num-done_trials_num)    # get the number of trials to run
        # run the trials
        for i in range(trial_len):
            design = designs[done_trials_num//trial_index]    # get the current design
            target = available_servers[i]
            cur_trial = done_trials_num % trial_index
            print(f'Runing {design}_{cur_trial} on {target}')
            subprocess.run(['ssh-keyscan', '-H', target], stdout=open(os.path.expanduser('~/.ssh/known_hosts'), 'a'))   # add the server to known_hosts
            command = f'cd {filedir}{design}_{cur_trial}.test/ && . set_paths.sh && make run_pnr-cts > output.txt 2>&1 &'
            subprocess.Popen(['ssh', target, command])
            done_trials_num += 1

        if done_trials_num < total_trials_num:
            # wait for 50 minutes to distribute remaining trials
            time.sleep(50*60)
   

