from Custom_Scheduler_class.Optimizer_class import Optimizer
from Custom_Scheduler_class.Scheduler_class import Scheduler
import asyncio
import time


async def main():
    fileaddress = '/user/stud/fall22/zm2404/E6693/project'
    env_command = "source '/courses/ee6693/code/python/miniconda3/bin/activate' 'adam_env'"
    # first get the server list
    scheduler = Scheduler(total_trials_num=40, username='zm2404', password='Mo183616', useless_list=[20])
    scheduler.first_rank_server(server_max_usage=12)

    pbounds = {"clk_period": [2.7, 5]}
    optimizer = Optimizer(initial_trials_num=20, total_trials_num=40, param_space=pbounds, metrics=['ADP'], func_coeff=[1])
    task1 = scheduler.rank_server(des_len=10, server_max_usage=12)
    task2 = optimizer.optimization(fileaddress=fileaddress, env_command=env_command, scheduler=scheduler, pyfile='da1_trial.py')
    await asyncio.gather(task1, task2)

if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print('Elapsed Time: ', end_time-start_time)
