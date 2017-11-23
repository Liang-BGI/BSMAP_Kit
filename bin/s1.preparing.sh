echo "job start at: $(date +%Y-%m-%d:%H:%M:%S)" && cat ../example/data/ref_genome/sample.genome.fa.gz | perl /usr/local/util/fasta2methBaseC.FT.pl > ../example/data/ref_genome/sample.genome.fa.gz.methBaseC.gz && echo "job end at: $(date +%Y-%m-%d:%H:%M:%S)"

