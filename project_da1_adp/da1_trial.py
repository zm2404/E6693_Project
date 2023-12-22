import argparse
import subprocess

import random
import time

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="A program that run specific set of parameters.")
    parser.add_argument('--clk_period', type=float, default=2.7, help='clk period')
    parser.add_argument('--max_tran_coef', type=float, default=0.3, help='set_max_transition [expr 0.3*$clk_period] [current_design]')
    parser.add_argument('--clk_tran_coef', type=float, default=0.1, help='set_clock_transition [expr 0.1*$clk_period] [get_clocks $clk_name]')
    parser.add_argument('--input_delay_coef', type=float, default=0.3, help='set_input_delay -max -clock [get_clocks $clk_name] [expr 0.3 * $clk_period] [remove_from_collection [all_inputs] [get_ports $clk_name]]')
    parser.add_argument('--output_delay_coef', type=float, default=0.3, help='set_output_delay -max -clock [get_clocks $clk_name] [expr 0.3 * $clk_period] [all_outputs]')
    parser.add_argument('--index', type=int, default=0, help='trial index')

    args = parser.parse_args()
    clk_period = round(args.clk_period, 2)
    max_tran_coef = round(args.max_tran_coef, 2)
    clk_tran_coef = round(args.clk_tran_coef, 2)
    input_delay_coef = round(args.input_delay_coef, 2)
    output_delay_coef = round(args.output_delay_coef, 2)
    index = args.index

    root_addrs = '/user/stud/fall22/zm2404/E6693/project'
    ####### copy the DA1 folder #######
    subprocess.run(['cp', '-r', f'{root_addrs}/DA1', f'{root_addrs}/DA1_{index}'])

    ####### modify the fpu_double.sdc file #######
    with open(f'{root_addrs}/DA1_{index}/SDC/fpu_double.sdc', 'r') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if "set clk_period" in lines[i]:
                lines[i] = f'set clk_period {clk_period}\n'
            if "set_max_transition [expr 0.3*$clk_period] [current_design]" in lines[i]:
                lines[i] = f'set_max_transition [expr {max_tran_coef}*$clk_period] [current_design]\n'
            if "set_clock_transition [expr 0.1*$clk_period] [get_clocks $clk_name]" in lines[i]:
                lines[i] = f'set_clock_transition [expr {clk_tran_coef}*$clk_period] [get_clocks $clk_name]\n'
            if "set_input_delay -max" in lines[i]:
                lines[i] = f'set_input_delay -max -clock [get_clocks $clk_name] [expr {input_delay_coef}*$clk_period] [remove_from_collection [all inputs] [get_ports $clk_name]]\n'
            if "set_output_delay -max" in lines[i]:
                lines[i] = f'set_output_delay -max -clock [get_clocks $clk_name] [expr {output_delay_coef}*$clk_period] [all_outputs]\n'
    

    with open(f'{root_addrs}/DA1_{index}/SDC/fpu_double.sdc', 'w') as file:
        file.writelines(lines)


    ####### run the design #######
    command = f'cd {root_addrs}/DA1_{index}/ && ./run.sh'
    #command = f'cd {root_addrs}/DA1_{index}/ && ls'

    print('Cadence running...')
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    stdout = result.stdout
    stderr = result.stderr

    # if no error, then collect the results
    if stderr != '':
        print(stderr)
        raise Exception('Error when running cadence')

    
    
    # collect the results
    REPORT_DIR = f'{root_addrs}/DA1_{index}/reports'
    REPORT_NAME = 'final_qor.rpt'
    
    try:
        with open(REPORT_DIR+'/'+REPORT_NAME, 'r') as file:
            for line in file:
                if 'Total Area' in line:
                    words = line.split()
                    AREA = words[-1]
                if 'clk' in line:
                    words = line.split()
                    if len(words) == 4:
                        SLACK = words[1]
        ADP = round(float(AREA) * clk_period, 2)
        SLACK_COST = round((float(SLACK)-10)**2)
    except:
        ADP = None
        SLACK_COST = None
 

    ####### write the results to a file #######
    resultdir = f'{root_addrs}/results/'
    resultfile = f'result_{index}.txt'

    with open(resultdir+resultfile, 'w') as file:
        file.write(f'ADP:{ADP}\nSLACK_COST:{SLACK_COST}')
    print(f'Trial {index} finished.')


    # ###### just for test ######
    # time_delay = [10, 15, 20]
    # tmdl = random.choice(time_delay)
    # time.sleep(tmdl)    # imitate running time of different parameter sets

    # epsilon = 1000000

    # filedir = '/user/stud/fall22/zm2404/E6693/project/results/'
    # filename = f'result_{index}.txt'

    # with open(filedir+filename, 'w') as file:
    #     file.write(f'epsilon:{epsilon}')
    # print(f'Trial {index} finished.')
