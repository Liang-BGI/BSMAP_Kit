#!/usr/bin/env python
# -*- coding:utf-8 -*-




'''

    Author: Hao Yu (yuhao@genomics.cn)
    Date:   2017-11-20  (v0.1)

'''




######## INTRODUCTION ########
#
#   This script is used to simplify the usage of BSMAP (Y Xi et al., 2009),
#   and make it as a workflow for large-scale analyzing of WGBS data
#
#   Author: Hao Yu
#   E-mail: yuhao@genomics.cn
#
##############################




######## PREPARE OPTIONS ########
#
#   This following function is used to prepare all the options for the jobs.
#
#   The usage of options is:
#       * The path of output directory (-o, --outdir), which default setting is "./"
#           You can assign the output pathname for your job and result generation place.
#
#       * The path to reference genome (-r, --ref_genome)
#           The option reference genome means the genome file for bsmap using
#
#       * The path to library set profile (-l, --libaray_set)
#           For the large-scale, we almost use a profile as storage to record the information between sample and data.
#           In our script, we suggest this profile should look like following format:
#   ===============================================================================================================================
#   SAMPLE    REPEAT_in_BIOLOGY    LIBRARY    LANE    INDEX_(barcode)    FILE_of_READ1                   FILE_of_READ2
#   -------------------------------------------------------------------------------------------------------------------------------
#   sample1   rep1                 lib1       lane1   1                  /path/lane1_lib1_1_1.fq.gz      /path/lane1_lib1_1_2.fq.gz
#   sample1   rep1                 lib1       lane1   2                  /path/lane1_lib1_2_1.fq.gz      /path/lane1_lib1_2_2.fq.gz
#   sample1   rep1                 lib1       lane1   3                  /path/lane1_lib1_3_1.fq.gz      /path/lane1_lib1_3_2.fq.gz
#   sample1   rep2                 lib2       lane1   1                  /path/lane1_lib2_1_1.fq.gz      /path/lane1_lib2_1_2.fq.gz
#   sample2   rep1                 lib3       lane1   1                  /path/lane1_lib3_1_1.fq.gz      /path/lane1_lib3_1_2.fq.gz
#   sample2   rep2                 lib3       lane2   1                  /path/lane2_lib3_1_1.fq.gz      /path/lane2_lib3_1_2.fq.gz
#   ===============================================================================================================================
#
#       * The path to toolset profile (-t, --toolset)
#           Our script employ all the usable tools from a profile of tools, in which tool name and its path are splited by "=",
#           and should look like following format:
#   =================================================================
#   TOOL_NAME              TOOL_PATH
#   -----------------------------------------------------------------
#   bsmap                = /usr/local/bin/bsmap
#   samtools             = /usr/local/bin/samtools
#   methratio            = /usr/local/util/methratio.py
#   binomialTest         = /usr/local/util/binomialTest.FT.r
#   methBaseC_Completing = /usr/local/util/methBaseC_Completing.FT.pl
#   CpG_Classifier       = /usr/local/util/CpG_Classifier.FT.pl
#   fasta2methBaseC      = /usr/local/util/fasta2methBaseC.FT.pl
#   =================================================================
#
#       * The path to parameter profile (-p, --parameter_set)
#           We collect the parameters involving all of our used tools, and assign a series of new names for them, and split their name and value by ":".
#           This work will make all of tools employed by our script as a union, and avoid the potential incompatibility of parameters among those tools.
#           In this release, we just flex a few of parameters for choosing, they should look like:
#   ======================
#   PARAMETER        VALUE
#   ----------------------
#   phred:           33
#   strand_specific: no
#   min_insert_size: 0
#   max_insert_size: 500
#   ======================
#
#       * Another parameter is involving the number of CPU thread (-n, --num_thread)
#           This parameter just affects the run-time in sorting of bam file (samtools sort).
#
#   In the end of function, it will return an OPTPARSE object.
#
#################################

def deal_option():
    import optparse

    parser = optparse.OptionParser()

    parser.add_option('-o', '--outdir', dest='outdir', metavar='DIR', help='assign the directory for output.  default: "./output"', default='./output')
    parser.add_option('-r', '--ref_genome', dest='ref_genome', metavar='FILE', help='assign the file path to reference genome file.')
    parser.add_option('-l', '--library_set', dest='library_set', metavar='FILE', help='assign the file path to library file.')
    parser.add_option('-t', '--toolset', dest='toolset', metavar='FILE', help='assign the file path to toolset file.')
    parser.add_option('-p', '--parameter_set', dest='parameter_set', metavar='FILE', help='assign the file path to parameter_set file.')
    parser.add_option('-n', '--num_thread', dest='num_thread', metavar='INT', help='assign the number of thread for "samtools sort".  default: 6', default=6)

    options, args = parser.parse_args()

    return options




######## FILE PARSE ########
#
#   The next three functhions are used to parse the profiles of library, toolset and paremeter set.
#   Each of them return a DICTIONARY object.
#
############################

def deal_library_set(library_path):
    try:
        profile = open(library_path, 'r')
    except IOError:
        print 'invalid File'
        exit(1)

    lib_info_box = {}
    for l in profile.readlines():
        sample, repeat, library, lane, index, read1, read2 = l.strip().split()

        if sample not in lib_info_box:
            lib_info_box.update({sample:{}})
        if repeat not in lib_info_box[sample]:
            lib_info_box[sample].update({repeat:{}})
        if library not in lib_info_box[sample][repeat]:
            lib_info_box[sample][repeat].update({library:{}})
        if lane not in lib_info_box[sample][repeat][library]:
            lib_info_box[sample][repeat][library].update({lane:{}})
        if index not in lib_info_box[sample][repeat][library][lane]:
            lib_info_box[sample][repeat][library][lane].update({index:[read1,read2]})

    return lib_info_box




def deal_toolset(toolset_path):
    try:
        profile = open(toolset_path, 'r')
    except IOError:
        print 'invalid File'
        exit(1)

    toolset_info_box = {}
    for l in profile.readlines():
        name, path = l.strip().split('=')
        name = name.strip()
        path = path.strip()

        if name not in toolset_info_box:
            toolset_info_box.update({name:path})

    return toolset_info_box




def deal_parameter_set(parameter_set_path):
    try:
        profile = open(parameter_set_path, 'r')
    except IOError:
        print 'Invalid File'
        exit(1)

    parameter_set_info_box = {}
    for l in profile.readlines():
        name, value = l.strip().split(':')
        name = name.strip()
        value = value.strip()

        if name not in parameter_set_info_box:
            parameter_set_info_box.update({name:value})

    return parameter_set_info_box




######## STEP ########
#
#   This function is used to construct the pipeline.
#
######################

def step(outdir, \
         ref_genome, library_set, phred, strand_specific, min_insert_size, max_insert_size, \
         bsmap, samtools, binomialTest, methBaseC_Completing, CpG_Classifier, fasta2methBaseC, num_thread):
    judge = {'yes':1, 'no':0}

    cmd0 = 'echo "job start at: $(date +%Y-%m-%d:%H:%M:%S)" && ' + \
           'cat ' + ref_genome + ' | perl ' + fasta2methBaseC + ' > ' + ref_genome + '.methBaseC.gz' + \
           ' && echo "job end at: $(date +%Y-%m-%d:%H:%M:%S)"\n'
    cmd1 = ''
    cmd2 = ''
    cmd3 = ''

    for sample in library_set:
        for repeat in library_set[sample]:
            for library in library_set[sample][repeat]:
                for lane in library_set[sample][repeat][library]:
                    for index in library_set[sample][repeat][library][lane]:
                        read1 = library_set[sample][repeat][library][lane][index][0]
                        read2 = library_set[sample][repeat][library][lane][index][1]

                        out_path = outdir + '/' + sample + '/' + repeat + '/' + library + '/' + lane + '/' + index

                        cmd1 += 'echo "job start at: $(date +%Y-%m-%d:%H:%M:%S)" && ' + \
                                'mkdir -p ' + out_path + \
                                ' && ' + bsmap + ' -d ' + ref_genome + ' -a ' + read1 + ' -b ' + read2 + \
                                ' -z ' + str(phred) + ' -n ' + str(judge[strand_specific]) + ' -m ' + str(min_insert_size) + ' -x ' + str(max_insert_size) + \
                                ' | ' + samtools + ' view -Sb -' + \
                                ' | ' + samtools + ' sort -@ ' + str(num_thread) + ' ' + out_path + '/' + lane + '_' + index + '.sort' + \
                                ' && ' + samtools + ' index ' + out_path + '/' + lane + '_' + index + '.sort.bam' + \
                                ' && ' + samtools + ' flagstat ' + out_path + '/' + lane + '_' + index + '.sort.bam > ' + out_path + '/' + lane + '_' + index + '.sort.bam.mappedRate' + \
                                ' && echo "job end at: $(date +%Y-%m-%d:%H:%M:%S)"\n'

                        cmd2 += 'echo "job start at: $(date +%Y-%m-%d:%H:%M:%S)" && ' + \
                                'python ' + methBaseC_Completing + \
                                ' -o ' + out_path + '/' + lane + '_' + index + '.methBaseC' + \
                                ' -d ' + ref_genome + \
                                ' -u -z -r -i correct ' + out_path + '/' + lane + '_' + index + '.sort.bam' + \
                                ' && cat ' + out_path + '/' + lane + '_' + index + '.methBaseC' + \
                                ' | Rscript ' + binomialTest + ' 0.9950' + \
                                ' | gzip -c > ' + out_path + '/' + lane + '_' + index + '.binTest.methBaseC.gz' + \
                                ' && gzip -cd ' + ref_genome + '.methBaseC.gz' + \
                                ' | perl ' + methBaseC_Completing + ' ' + out_path + '/' + lane + '_' + index + '.binTest.methBaseC.gz' + \
                                ' | perl ' + CpG_Classifier + ' ' + out_path + '/' + lane + '_' + index + '.binTest.methBaseC' + \
                                ' | gzip -c > ' + out_path + '/' + lane + '_' + index + '.binTest.methBaseC.cmp.gz' + \
                                ' && echo "job end at: $(date +%Y-%m-%d:%H:%M:%S)"\n'

                        cmd3 += 'echo "cleaning temporary files ..." && ' + \
                                'rm -f ' + out_path + '/' + lane + '_' + index + '.methBaseC ' + out_path + '/' + lane + '_' + index + '.binTest.methBaseC.gz' + \
                                ' && echo "cleaning is accomplished"\n'

    return (cmd0, cmd1, cmd2, cmd3)




######## MAIN ########
#
#   Following is the running body of our script.
#
######################

if __name__ == '__main__':
    try:
        option = deal_option()

        outdir = option.outdir
        ref_genome = option.ref_genome
        library_set = deal_library_set(option.library_set)
        toolset = deal_toolset(option.toolset)
        parameter_set = deal_parameter_set(option.parameter_set)

        bsmap = toolset['bsmap']
        samtools = toolset['samtools']
        methratio = toolset['methratio']
        binomialTest = toolset['binomialTest']
        methBaseC_Completing = toolset['methBaseC_Completing']
        CpG_Classifier = toolset['CpG_Classifier']
        fasta2methBaseC = toolset['fasta2methBaseC']
        
        phred = parameter_set['phred']
        strand_specific = parameter_set['strand_specific']
        min_insert_size = parameter_set['min_insert_size']
        max_insert_size = parameter_set['max_insert_size']

        num_thread = option.num_thread

        command = step(outdir, \
                       ref_genome, library_set, phred, strand_specific, min_insert_size, max_insert_size, \
                       bsmap, samtools, binomialTest, methBaseC_Completing, CpG_Classifier, fasta2methBaseC, num_thread)

        script0 = open('s1.preparing.sh', 'w')
        script1 = open('s2.mapping.sh', 'w')
        script2 = open('s3.bam2base.sh', 'w')
        script3 = open('s4.cleaning.sh', 'w')
        print >> script0, command[0],
        print >> script1, command[1],
        print >> script2, command[2],
        print >> script3, command[3],
        script0.close()
        script1.close()
        script2.close()
        script3.close()
    except TypeError:
        print 'please use option -h for help'
        exit(1)
