import paramiko
import asyncio

class Scheduler:
    def __init__(self, total_trials_num, username, password):
        '''
        total_trials_num: the maximum number of trials we want to run
        username and password: the username and password of the EE account
        '''

        self.total_trials_num = total_trials_num
        self.username = username
        self.password = password
        self.done_trials_num = 0
        self.available_servers = []


    def first_rank_server(self, server_max_usage:int=10) -> list:
        '''
        This function is to rank the servers at the beginning, it runs only once.
        '''
        info = self.get_multiple_load(self.username, self.password)    # get the load of all the servers
        sorted_info = sorted(info.items(), key=lambda x: x[1])

        max_len = len(info)

        ranked_servers = []
        for i in range(max_len):
            multi_serv_n = max(int(server_max_usage-sorted_info[i][1]), 0)
            ranked_servers.extend([self.process_int(sorted_info[i][0])]*multi_serv_n)

        real_len = min(len(ranked_servers), self.total_trials_num)
        sorted_server_list = ranked_servers[:real_len]
        self.available_servers = sorted_server_list
        

    async def rank_server(self, des_len:int|str='all', server_max_usage:int=10) -> list:
        '''
        This function will collect the load of all the servers, and determine which server to use.
        It will return a list of server ranked in order of idleness
        len: number of servers we need
        server_max_usage: the maximum usage of a server we want to use. (leave some space for other users)
        '''
        
        while True:
            await asyncio.sleep(120)   # update every 2 minutes
            if self.done_trials_num >= self.total_trials_num:
                break
            #info = self.get_multiple_load(self.username, self.password)    # get the load of all the servers
            info = await asyncio.to_thread(self.get_multiple_load, self.username, self.password)    # get the load of all the servers

            # sort the servers by their load
            # sorted sweeps each tuple info.items() returns, and rank those tuples accodring to 'key', 
            # which is a lambda function indicating using the second element of each tuple
            sorted_info = sorted(info.items(), key=lambda x: x[1])

            # Get the max number machines
            if isinstance(des_len, str):
                if des_len == 'all':
                    max_len = len(info)
                else:
                    raise Exception("variable len should be either an integer or 'all'.")
            else:
                max_len = min(len(info), des_len)   # get the number of servers we need

            ranked_servers = []
            for i in range(max_len):
                multi_serv_n = max(int(server_max_usage-sorted_info[i][1]), 0)  # get the available usage, if available usage is not enough, get 0.
                ranked_servers.extend([self.process_int(sorted_info[i][0])]*multi_serv_n)

            res_trials = self.total_trials_num - self.done_trials_num
            real_len = min(len(ranked_servers), res_trials) # get the number of servers we actually need regarding the number of residual trials
            sorted_server_list = ranked_servers[:real_len]
            self.available_servers = sorted_server_list
            print(sorted_server_list)
            if self.done_trials_num >= self.total_trials_num:
                break
            #await asyncio.sleep(1800)   # update every 30 minutes


    def get_multiple_load(self, username, password) -> dict:
        info = {}
        for i in range(1,43):   # we have 42 servers
            try:
                if i < 10:
                    target = 'cadpc0' + str(i) + '.ee.columbia.edu'
                else:
                    target = 'cadpc' + str(i) + '.ee.columbia.edu'
                filename = 'load' + str(i) + '.txt'
                load_info = self.get_single_load(username, password, target, filename)
                info[i] = self.weighted_load(load_info['load'], load_info['cpu'])
                #print('Done with ' + target)
            except:
                print('Error with ' + target)
        print('Done getting load info')
        return info
    

    def get_single_load(self, username, password, target, filename) -> dict:
        '''
        This function is to get the load of the [target] server.
        It uses the paramiko library to ssh into the server and run the command 'top'.
        It saves the output to a text file, file name is specified by [filename].

        The output is a dictionary with two keys: 'load' and 'cpu'.
        '''

        filedir = './load_output/'

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's key
        ssh_client.connect(target, username=username, password=password)

        stdin, stdout, stderr = ssh_client.exec_command('top -n 1 -b')	# change the command
        output = stdout.read().decode()

        load_output = []
        lines = output.split('\n')
        info = {}
        for i in range(len(lines)):
            if 'load average' in lines[i]:
                load_output.append(lines[i])
                info['load'] = lines[i].split('load average: ')[1].split(',')
            if 'Tasks' in lines[i]:
                load_output.append(lines[i])
            if '%CPU' in lines[i]:  # 这里只获取了一个cpu的用量，但是不一定只有一个人再用，所以要获取多个。那么获取几个呢？
                load_output.append(lines[i])
                load_output.append(lines[i+1])
                info['cpu'] = lines[i+1].split()[8]

        load_output = '\n'.join(load_output)

        # Save the output to a text file
        with open(filedir+filename, 'w') as file:
            file.write(load_output)

        ssh_client.close()

        return info
    

    def weighted_load(self, load:list, cpu) -> float:
        '''
        This function will calculate the weighted load of a server.
        '''
        load = [float(x) for x in load]
        cpu = float(cpu)
        return 0.7*load[0] + 0.2*load[1] + 0.1*load[2] + 0.01*cpu
    

    def process_int(self, n:int) -> str:
        if n < 10:
            return '0'+str(n)
        return str(n)
    
