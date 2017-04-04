#!/bin/bash
while getopts j:p:d:e:t:o: option
do
        case "${option}"
        in
                j) jar=${OPTARG};;
                p) peptides=${OPTARG};;
                d) database=${OPTARG};;
                e) evalue=${OPTARG};;
                t) threshold=${OPTARG};;
                o) output=${OPTARG};;
        esac
done

tmp="tmp"$RANDOM
rm -f $output
mkdir $tmp
mkdir $tmp/fasta
mkdir $tmp/pssm
awk -v tmp=$tmp '/^>/ {OUT=tmp"/fasta/"substr($1,2) ".fa"}; {print >> OUT; close(OUT)}' $peptides
for file in $(ls $tmp/fasta)
do
	queryid=$(basename ${file%.*})
	psiblast -db $database -query $tmp/fasta/$file -outfmt 6  -out_ascii_pssm $tmp/pssm/$file.pssm -evalue 1e-5 -inclusion_ethresh 1e-5 -num_iterations 3 -seg no -use_sw_tback -num_threads 16 >> psiblast.out ;
	java -jar $jar/tmseg.jar  -i $tmp/fasta/$file -p $tmp/pssm/$file.pssm -o query.out;
	#grep -v '^#' query.out >> $output
	result=$(tail -1 query.out)
	hstart=$(echo $result | grep -ob H | head -1 | grep -oE '[0-9]+')
	hend=$(echo $result | grep -ob H | tail -1 | grep -oE '[0-9]+')
	hcount=$(grep -c TRANSMEM query.out)
	pattern=$(echo $result | perl -pe 's/1/o/g;' -pe 's/2/i/g;' -pe 's/((H)\2+)/$-[2]."-".$+[1]/ge;' -pe 's/o+/o/g;' -pe 's/i+/i/g')
	if [  "$hcount" -gt 0 ]
		then echo -e $queryid '\ttmseg\ttransmembrane helices\t'$hstart '\t' $hend '\t' $hcount '\t.\t.\tNote='$pattern >> $output;
	fi
done;
rm -rf $tmp
