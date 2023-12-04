import asyncio
import asyncssh
import random
import subprocess


class Trial:
    def __init__(self, alpha, beta, trial_index):
        self.alpha = alpha
        self.beta = beta
        self.trial_index = trial_index
        self.result = None

    async def demo_run(self):
        time_delay = [5,10,15]
        tmdl = random.choice(time_delay)
        await asyncio.sleep(tmdl)    # imitate running time of different parameter sets
        return -(self.alpha**2 + self.beta**2), {"alpha":self.alpha,"beta":self.beta}
    
    async def run(self):
        '''
        This function run the commend on local machine.
        '''
        command = f"python sample_cadence.py --alpha {self.alpha} --beta {self.beta} --index {self.trial_index}"    # TODO: change the command
        process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            print(f'{stdout.decode().strip()}', f'{self.alpha}, {self.beta}')
            with open(f'./results/result_{self.trial_index}.txt', 'r') as file:
                self.result = float(file.read().split(':')[1])  # 具体读取方法再改
            return self.result, {"alpha":self.alpha,"beta":self.beta}
    

    async def run_remote(self, scheduler):
        '''
        This function run the commend on remote machine.
        '''
        while not scheduler.available_servers:
            await asyncio.sleep(30)

        server = scheduler.available_servers.pop(0)
        target = 'cadpc' + str(server) + '.ee.columbia.edu'
        # connect to the server
        try:
            async with asyncssh.connect(host = target, username = scheduler.username, password = scheduler.password) as conn:
                #command = "cd /user/stud/fall22/zm2404/E6693/project/;"
                command = f"python3 /user/stud/fall22/zm2404/E6693/project/sample_cadence.py --alpha {self.alpha} --beta {self.beta} --index {self.trial_index}"
                result = await conn.run(command, check=True)
                #print(result.stderr.strip())
                print(f'{target}: {result.stdout.strip()}', f'{self.alpha}, {self.beta}')
                with open(f'./results/result_{self.trial_index}.txt', 'r') as file:
                    self.result = float(file.read().split(':')[1])  # 具体读取方法再改
                scheduler.done_trials_num += 1
                scheduler.available_servers.append(server)  # put the server back to the list
                return self.result, {"alpha":self.alpha,"beta":self.beta}
        except:
            print(f'Error with {target}')
            await self.run_remote(scheduler)
    