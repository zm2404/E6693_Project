set sdc_version 1.6

current_design fpu_double

set clk_period 3.22
set clk_name   "clk" 

create_clock -name $clk_name -add -period $clk_period [get_ports $clk_name]

set_max_transition [expr 0.3*$clk_period] [current_design]
set_max_transition [expr 0.1*$clk_period] [get_clocks $clk_name] -clock_path
set_clock_transition [expr 0.1*$clk_period] [get_clocks $clk_name]

set_input_delay -max -clock [get_clocks $clk_name] [expr 0.3*$clk_period] [remove_from_collection [all inputs] [get_ports $clk_name]]
set_input_delay -min -clock [get_clocks $clk_name] [expr 0.0 * $clk_period] [remove_from_collection [all_inputs] [get_ports $clk_name]]

set_output_delay -max -clock [get_clocks $clk_name] [expr 0.3*$clk_period] [all_outputs]
set_output_delay -min -clock [get_clocks $clk_name] [expr 0.0 * $clk_period] [all_outputs]

