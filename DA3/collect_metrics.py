import pandas as pd

def relative_change_based_cost_function(metrics, weight):
    '''
    Since the table has given that lower scores are better for all metrics,
    all metrics have the '-' polarity
    '''
    ref_cts_delay = metrics['cts.delay'][0]
    print('ref_cts_delay: ', ref_cts_delay)
    ref_cts_power = metrics['cts.power'][0]
    print('ref_cts_power: ', ref_cts_power)
    ref_cts_area = metrics['cts.design.area'][0]
    print('ref_cts_area: ', ref_cts_area)
    cost = (metrics['cts.delay']-ref_cts_delay)/ref_cts_delay*weight[0]
    cost += (metrics['cts.power']-ref_cts_power)/ref_cts_power*weight[1]
    cost += (metrics['cts.design.area']-ref_cts_area)/ref_cts_area*weight[2]

    print('cost: \n', cost)
    metrics['relative change based cost function'] = cost


def normalization_cost_function(metrics, weight):
    '''
    Since the table has given that lower scores are better for all metrics,
    all metrics have the '-' polarity
    '''
    norm_cts_delay = (metrics['cts.delay'] - metrics['cts.delay'].min())/(metrics['cts.delay'].max()-metrics['cts.delay'].min())
    norm_cts_power = (metrics['cts.power'] - metrics['cts.power'].min())/(metrics['cts.power'].max()-metrics['cts.power'].min())
    norm_cts_area = (metrics['cts.design.area'] - metrics['cts.design.area'].min())/(metrics['cts.design.area'].max()-metrics['cts.design.area'].min())
    cost = norm_cts_delay*weight[0] + norm_cts_power*weight[1] + norm_cts_area*weight[2]

    metrics['normalization cost function'] = cost



designs = ['blabla-da3', 'salsa20-da3']
trial_num = 12
all_data = pd.DataFrame()    # Create empty dataframe

weights = [[1,1,1], [3,2,1]]

for weight in weights:              # two weights
    for i in range(2):              # two cost function
        for design in designs:
            all_data_temp = pd.DataFrame()    # Create empty dataframe
            if design == 'blabla-da3':
                clk_period = 0.9        # ns
            else:
                clk_period = 0.95       # ns
            ######## Read metrics.csv and add necessary information ########
            for trial_index in range(trial_num):
                csv_file = f'./{design}_{trial_index}.test/metrics/metrics.csv'
                with open(f'./{design}_{trial_index}.test/annotation.txt', 'r') as f:
                    annotation = f.read()
                try:
                    df = pd.read_csv(csv_file)
                    print('Read file: '+csv_file)
                    cts_delay = clk_period - df['cts.timing.setup.wns.path_group:reg2reg']
                    print('cts_delay: ', cts_delay)
                    cts_delay_index = df.columns.get_loc('cts.timing.setup.wns.path_group:reg2reg') + 1
                    df.insert(cts_delay_index, 'clk_period', clk_period)                        # insert clk_period to the dataframe
                    df.insert(cts_delay_index+1, 'cts.delay', cts_delay)                        # insert cts_delay to the dataframe
                    df.insert(0, 'trial', annotation)                                           # add annotation to the first column
                    all_data_temp = all_data_temp.append(df, ignore_index=True, sort=False)     # add to the main dataframe
                except Exception as e:
                    print('Cannot read file: '+csv_file+' ', e)
            
            ###################### Add cost function ######################
            if i == 0:
                relative_change_based_cost_function(all_data_temp, weight)
                all_data_temp.sort_values(by=['relative change based cost function'])
            else:
                normalization_cost_function(all_data_temp, weight)
                all_data_temp.sort_values(by=['normalization cost function'])

            #################### Add to the main df ######################
            all_data = all_data.append(all_data_temp, ignore_index=True, sort=False)    # add to the main dataframe
            all_data = all_data.append({}, ignore_index=True, sort=False)               # add an empty row
        
        all_data = all_data.append({}, ignore_index=True, sort=False)                   # add an empty row
    
    all_data = all_data.append({}, ignore_index=True, sort=False)                       # add an empty row
        

excel_file = 'all_trials_metrics.xlsx'
all_data.to_excel(excel_file, index=False) 