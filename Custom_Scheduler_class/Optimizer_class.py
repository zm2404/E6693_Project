from bayes_opt import BayesianOptimization, UtilityFunction
import asyncio
from .Trial_class_demo import Trial
import os


class Optimizer:
    def __init__(self, initial_trials_num, total_trials_num, param_space, metrics, func_coeff, func_power=None, random_initial:bool=True, utility_type:str='ucb', kappa:float=1.96, xi:float=0.01):
        '''
        initial_trials_num: the number of trials we want to run at the beginning
        param_space: the space of parameters we want to optimize
        utility_type: the type of utility function we want to use
        kappa: the parameter of ucb
        xi: the parameter of ucb
        '''
        self.initial_trials_num = initial_trials_num    # initial number of trials
        self.total_trials_num = total_trials_num        # total number of trials
        self.done_trials_num = 0                        # number of trials that have been done
        self.gend_trials_num = initial_trials_num       # number of trials that have been generated
        self.param_space = param_space
        self.random_initial = random_initial
        self.utility_type = utility_type
        self.kappa = kappa
        self.xi = xi
        self.metrics = metrics                          # the metrics used in the objective function
        self.func_coeff = func_coeff                    # the coefficients of the metrics
        if func_power is None:
            self.func_power = [1]*len(metrics)
        else:
            self.func_power = func_power                # the power of the metrics
        #self.optimizer = BayesianOptimization(f=None, pbounds=param_space, verbose=2)
        #self.utility = UtilityFunction(kind=utility_type, kappa=kappa, xi=xi)
        self._input_key_order = list(param_space.keys())

    
    def random_param(self,optimizer,utility):
        '''
        define the random initial points
        '''
        sorted_initial_points = []
        initial_points = [optimizer.suggest(utility) for _ in range(self.initial_trials_num)]
        for i in range(self.initial_trials_num):
            sorted_initial_points.append({key: initial_points[i][key] for key in self._input_key_order})
            sorted_initial_points[i]['trial_index'] = i
        return sorted_initial_points
    

    async def black_box_function(self, param, fileaddress, scheduler=None, pyfile='sample_cadence.py') -> tuple[float, dict]:
        '''
        define the black box function
        '''
        trial = Trial(param)
        if scheduler is None:
            result = await trial.run()
        else:
            result = await trial.run_remote(scheduler, pyfile=pyfile, fileaddress=fileaddress)

        if result is None:
            self.done_trials_num += 1
            return None, None

        # calculate the cost
        cost = 0
        for i in range(len(self.metrics)):
            cost += self.func_coeff[i] * (result[0][self.metrics[i]] ** self.func_power[i])
        result = (-1*cost, result[1])
        self.done_trials_num += 1
        return result


    async def optimization(self, fileaddress, initial_points:list=None, scheduler=None, pyfile:str='sample_cadence.py'):
        '''
        fileaddress:        the root address of the pyfile
        initial_points:     the initial points we want to use
        scheduler:          the scheduler we want to use
        pyfile:             the name of the pyfile

        for example: sample_cadence.py is at /user/stud/fall22/zm2404/E6693/project/sample_cadence.py
        fileaddress = '/user/stud/fall22/zm2404/E6693/project'
        pyfile = 'sample_cadence.py'
        '''

        # define the optimizer and utility function
        optimizer = BayesianOptimization(f=None, pbounds=self.param_space, verbose=2, random_state=1234, allow_duplicate_points=True)
        utility = UtilityFunction(kind=self.utility_type, kappa=self.kappa, xi=self.xi)

        # create results folder
        if not os.path.exists(f'{fileaddress}/results'):
            os.makedirs(f'{fileaddress}/results')

        if self.random_initial:
            initial_points = self.random_param(optimizer,utility)
        else:
            initial_points = initial_points

        for param in initial_points:
            print('Optimizer: ',param)
        trials = [asyncio.create_task(self.black_box_function(param=param, fileaddress=fileaddress, scheduler=scheduler, pyfile=pyfile)) for param in initial_points]

        while self.done_trials_num < self.total_trials_num:
            done, _ = await asyncio.wait(trials, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                print('Optimizer: have done: ', self.done_trials_num)
                result = await task
                print(result)
                try:
                    print('Optimizer: Register the result.')
                    optimizer.register(params=result[1], target=result[0])
                except Exception as e:
                    print(f'Optimizer: Error in optimizer registration: {e}')

                if self.gend_trials_num < self.total_trials_num:
                    print('Optimizer: Generate new parameters.')
                    next_point = optimizer.suggest(utility)
                    sorted_next_point = {key: next_point[key] for key in self._input_key_order}
                    sorted_next_point['trial_index'] = self.gend_trials_num
                    new_task = asyncio.create_task(self.black_box_function(param=sorted_next_point, fileaddress=fileaddress, scheduler=scheduler, pyfile=pyfile))
                    self.gend_trials_num += 1
                    trials.append(new_task)
                
                trials.remove(task)

        print('Optimization finished.')
        print("Best result: {}; f(x) = {:.3f}.".format(optimizer.max["params"], optimizer.max["target"]))