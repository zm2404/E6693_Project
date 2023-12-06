from bayes_opt import BayesianOptimization, UtilityFunction
import asyncio
from .Trial_class_demo import Trial

class Optimizer:
    def __init__(self, initial_trials_num, total_trials_num, param_space, random_initial:bool=True, utility_type:str='ucb', kappa:float=1.96, xi:float=0.01):
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
        # self.metrics = metrics                          # the metrics used in the objective function
        # self.func_coeff = func_coeff                    # the coefficients of the metrics
        # if func_power is None:
        #     self.func_power = [1]*len(metrics)
        # else:
        #     self.func_power = func_power                # the power of the metrics
        #self.optimizer = BayesianOptimization(f=None, pbounds=param_space, verbose=2)
        #self.utility = UtilityFunction(kind=utility_type, kappa=kappa, xi=xi)

    
    def random_param(self,optimizer,utility):
        '''
        define the random initial points
        '''

        initial_points = [optimizer.suggest(utility) for _ in range(self.initial_trials_num)]
        for i in range(self.initial_trials_num):
            initial_points[i]['trial_index'] = i
        return initial_points
    

    async def black_box_function(self, param, scheduler=None, pyfile='sample_cadence.py') -> tuple[float, dict]:
        '''
        define the black box function
        '''
        trial = Trial(**param)
        if scheduler is None:
            result = await trial.run()
        else:
            result = await trial.run_remote(scheduler, pyfile=pyfile)

        # # calculate the cost
        # metrics = result[0]
        # cost = 0
        # for i in range(len(self.metrics)):
        #     cost += self.func_coeff[i] * metrics[self.metrics[i]] ** self.func_power[i]
        # result = (-1*cost, result[1])
        self.done_trials_num += 1
        return result


    async def optimization(self, initial_points:list=None, scheduler=None, pyfile:str='sample_cadence.py'):
        optimizer = BayesianOptimization(f=None, pbounds=self.param_space, verbose=2, random_state=1234, allow_duplicate_points=True)
        utility = UtilityFunction(kind=self.utility_type, kappa=self.kappa, xi=self.xi)

        if self.random_initial:
            initial_points = self.random_param(optimizer,utility)
        else:
            initial_points = initial_points

        trials = [asyncio.create_task(self.black_box_function(param, scheduler, pyfile)) for param in initial_points]

        while self.done_trials_num < self.total_trials_num:
            done, _ = await asyncio.wait(trials, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                print('have done: ', self.done_trials_num)
                result = await task
                print(result)
                try:
                    print('Generate new parameters.\n')
                    optimizer.register(params=result[1], target=result[0])
                except Exception as e:
                    print(f'Error in optimizer registration: {e}')

                if self.gend_trials_num < self.total_trials_num:
                    next_point = optimizer.suggest(utility)
                    next_point['trial_index'] = self.gend_trials_num
                    new_task = asyncio.create_task(self.black_box_function(next_point, scheduler))
                    self.gend_trials_num += 1
                    trials.append(new_task)
                
                trials.remove(task)

        print('Optimization finished.\n')
        print("Best result: {}; f(x) = {:.3f}.".format(optimizer.max["params"], optimizer.max["target"]))




    