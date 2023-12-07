#name="blabla" #sala
#path = "../git_code/input/plugs/"
for((m=1;m<=6;m++))
do
 case $m in
  1)
   let L=8;
   filename="slack"
  ;;
  2)
   let L=20;
   filename="failpath"
  ;;
  3)
   let L=22;
   filename="total_cell_area"
  ;;
  4)
   let L=24;
   filename="total_instances"
  ;;
  5)
   let L=55;
   filename="fpu_double"
  ;;
  6)
   let L=71;
   filename="subtotal"
  ;;
 esac
for((v=1;v<=8;v++))
do
 for((i=1; i<=10; i=i+2))
 do
 output_name="final_"$v"_"$i
  sed -n "$L p" ../metric_data/${output_name}.rpt >> ../metric/${filename}.txt
  #echo "L=$L"
 done #done for i
 echo -e '\n' >> ../metric/${filename}.txt
done #done for v

done #done for m
echo "test all done"
