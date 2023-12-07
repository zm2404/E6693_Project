#name="blabla" #sala
#path = "../git_code/input/plugs/"


for((v=1;v<=8;v++))
do
 for((i=1; i<=10; i=i+2))
 do
	source ../DA1/clean.sh
  case $v in
    1)
	origin="set clk_period 1"
	var=$(echo "scale=2; ( $i - 1 ) * 5 / 10 + 1" | bc)
	#echo "$i,this is $var"
	aft="set clk_period "$var
	echo "$i,$aft"
	sed -i "5 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "5 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
    2)
	origin="expr 0.3"
	var=$(echo "scale=2; $i / 10" | bc)
	#echo "$i,this is $var"
	aft="expr "$var
	sed -i "10 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "10 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
    3)
	origin="expr 0.1"
	var=$(echo "scale=2; $i / 10" | bc)
	#echo "$i,this is $var"
	aft="expr "$var
	sed -i "11 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "11 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
    4)
	origin="expr 0.1"
	var=$(echo "scale=2; $i / 10" | bc)
	#echo "$i,this is $var"
	aft="expr "$var
	sed -i "12 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "12 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
    5)
	origin="expr 0.3"
	var=$(echo "scale=2; $i / 10" | bc)
	#echo "$i,this is $var"
	aft="expr "$var
	sed -i "14 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "14 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
    6)
	origin="expr 0.0"
	var=$(echo "scale=2; $i / 10" | bc)
	#echo "$i,this is $var"
	aft="expr "$var
	sed -i "15 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "15 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
    7)
	origin="expr 0.3"
	var=$(echo "scale=2; $i / 10" | bc)
	#echo "$i,this is $var"
	aft="expr "$var
	sed -i "17 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "17 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
    8)
	origin="expr 0.0"
	var=$(echo "scale=2; $i / 10" | bc)
	#echo "$i,this is $var"
	aft="expr "$var
	sed -i "18 s/$origin/$aft/g" ../DA1/SDC/fpu_double.sdc
	source ../DA1/run.sh
	sed -i "18 s/$aft/$origin/g" ../DA1/SDC/fpu_double.sdc
    ;;
  esac
	output_name="final_"$v"_"$i
	cp ../DA1/reports*/final.rpt ../metric_data/${output_name}.rpt
	echo "final_area.rpt" >> ../metric_data/${output_name}.rpt
	sed -n "10p" ../DA1/reports*/final_area.rpt >> ../metric_data/${output_name}.rpt
	sed -n "11p" ../DA1/reports*/final_area.rpt >> ../metric_data/${output_name}.rpt
	sed -n "12p" ../DA1/reports*/final_area.rpt >> ../metric_data/${output_name}.rpt
	sed -n "13p" ../DA1/reports*/final_area.rpt >> ../metric_data/${output_name}.rpt
	sed -n "14p" ../DA1/reports*/final_area.rpt >> ../metric_data/${output_name}.rpt
	echo "final_power.rpt" >> ../metric_data/${output_name}.rpt
	sed -n "4p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "5p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "6p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "7p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "8p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "9p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "10p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "11p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "12p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "13p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "14p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "15p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "16p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt	
	sed -n "17p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
	sed -n "18p" ../DA1/reports*/final_power.rpt >> ../metric_data/${output_name}.rpt
    # *)
    #;;
 done #done for i
	echo "done for v=$v"
done #done for v

echo "test all done"
