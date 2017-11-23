#!/usr/bin/env perl


use strict;
use warnings;


my ($n1, $cg1, $chg1, $chh1, $chn1, $cng1, $cnh1, $cnn1) = (0, 0, 0, 0, 0, 0, 0, 0);
my ($n5, $cg5, $chg5, $chh5, $chn5, $cng5, $cnh5, $cnn5) = (0, 0, 0, 0, 0, 0, 0, 0);

printf STDOUT "#1.chr\t2.pos\t3.strand\t4.context\t5.type\t6.ratio\t7.C_count\t8.CT_count\t9.rev_G_count\t10.rev_GA_count\t11.p-value\t12.FDR_p-value\n";

while (<STDIN>)
{
        next if m/^#/ or m/context/;
        chomp;

        my @line  = split /\s+/;
        $line[4]  = 0 if $line[4]  eq 'NA';
        $line[6]  = 0 if $line[6]  eq 'NA';
        $line[7]  = 0 if $line[7]  eq 'NA';
        $line[8]  = 0 if $line[8]  eq 'NA';
        $line[9]  = 0 if $line[9]  eq 'NA';
        $line[10] = 0 if $line[10] eq 'NA';
        $line[11] = 0 if $line[11] eq 'NA';

        my $chr = $line[0];
        my $pos = $line[1];
        my $std = $line[2];
        my $ctx = $line[3];
        my $typ;
           $typ = 'CG'  if ($std eq '+' and $ctx =~ m/\S\SCG\S/)            or ($std eq '-' and $ctx =~ m/\SCG\S\S/);
           $typ = 'CHH' if ($std eq '+' and $ctx =~ m/\S\SC[A|T|C][A|T|C]/) or ($std eq '-' and $ctx =~ m/[A|T|G][A|T|G]G\S\S/);
           $typ = 'CHG' if ($std eq '+' and $ctx =~ m/\S\SC[A|T|C]G/)       or ($std eq '-' and $ctx =~ m/C[A|T|G]G\S\S/);
           $typ = 'CHN' if ($std eq '+' and $ctx =~ m/\S\SC[A|T|C]N/)       or ($std eq '-' and $ctx =~ m/N[A|T|G]G\S\S/);
           $typ = 'CNH' if ($std eq '+' and $ctx =~ m/\S\SCN[A|T|C]/)       or ($std eq '-' and $ctx =~ m/[A|T|G]NG\S\S/);
           $typ = 'CNG' if ($std eq '+' and $ctx =~ m/\S\SCNG/)             or ($std eq '-' and $ctx =~ m/CNG\S\S/);
           $typ = 'CNN' if ($std eq '+' and $ctx =~ m/\S\SCNN/)             or ($std eq '-' and $ctx =~ m/NNG\S\S/);
        my $ra  = $line[4];
        my $c   = $line[6];
        my $ct  = $line[7];
        my $g   = $line[8];
        my $ga  = $line[9];
        my $p   = $line[10];
        my $fdr = $line[11];

        if ((sprintf "%.4f", $fdr) <= 0.05)
        {
                if ($ct >= 1)
                {
                        $n1 ++;

                        $cg1  ++ if $typ eq 'CG';
                        $chg1 ++ if $typ eq 'CHG';
                        $chh1 ++ if $typ eq 'CHH';
                        $chn1 ++ if $typ eq 'CHN';
                        $cng1 ++ if $typ eq 'CNG';
                        $cnh1 ++ if $typ eq 'CNH';
                        $cnn1 ++ if $typ eq 'CNN';
                }

                if ($ct >= 5)
                {
                        $n5 ++;

                        $cg5  ++ if $typ eq 'CG';
                        $chg5 ++ if $typ eq 'CHG';
                        $chh5 ++ if $typ eq 'CHH';
                        $chn5 ++ if $typ eq 'CHN';
                        $cng5 ++ if $typ eq 'CNG';
                        $cnh5 ++ if $typ eq 'CNH';
                        $cnn5 ++ if $typ eq 'CNN';
                }
        }

        printf STDOUT "%s\t%d\t%s\t%s\t%s\t%.3f\t%d\t%d\t%d\t%d\t%.3e\t%.3e\n",
                       $chr, $pos, $std, $ctx, $typ, $ra, $c, $ct, $g, $ga, $p, $fdr;
}

open OUT, '>', "$ARGV[0].stat";
printf OUT "C sites component under 1x depth (TOTAL_NUM, CG, CHG, CHH, CHN, CNG, CNH, CNN): %10d, %10d, %10d, %10d, %10d, %10d, %10d, %10d\n",
            $n1, $cg1, $chg1, $chh1, $chn1, $cng1, $cnh1, $cnn1;
printf OUT "C sites component under 5x depth (TOTAL_NUM, CG, CHG, CHH, CHN, CNG, CNH, CNN): %10d, %10d, %10d, %10d, %10d, %10d, %10d, %10d\n",
            $n5, $cg5, $chg5, $chh5, $chn5, $cng5, $cnh5, $cnn5;
close OUT;
