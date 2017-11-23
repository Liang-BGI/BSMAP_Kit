#!/usr/bin/env perl


use strict;
use warnings;


printf STDOUT "#1.chr\t2.pos\t3.strand\t4.context\t5.ratio\t6.eff_CT_count\t7.C_count\t8.CT_count\t9.rev_G_count\t10.rev_GA_count\t11.p-value\t12.FDR_p-value\n";

$/ = "\>"; <STDIN>; $/ = "\n";
while (<STDIN>)
{
        my $scf = $_;   chomp $scf; $/ = "\>";
        my $seq = <STDIN>; chomp $seq; $/ = "\n"; $seq =~ s/\n//g;

        my @seq_stream = split //, $seq;
        my $pos = 0;
        map
        {
                $pos ++;

                if ($_ eq 'C' or $_ eq 'c' or $_ eq 'G' or $_ eq 'g')
                {
                        my ($ctx1, $ctx2, $ctx3, $ctx4, $ctx5);
                            $ctx1 = 'N' if $pos - 2 < 1;           $ctx1 = $seq_stream[$pos - 1 - 2] if $pos - 2 >= 1;
                            $ctx2 = 'N' if $pos - 1 < 1;           $ctx2 = $seq_stream[$pos - 1 - 1] if $pos - 1 >= 1;
                            $ctx3 = $seq_stream[$pos - 1];
                            $ctx4 = 'N' if $pos + 1 > @seq_stream; $ctx4 = $seq_stream[$pos - 1 + 1] if $pos + 1 <= @seq_stream;
                            $ctx5 = 'N' if $pos + 2 > @seq_stream; $ctx5 = $seq_stream[$pos - 1 + 2] if $pos + 2 <= @seq_stream;

                        my $std;
                           $std = '+' if $_ eq 'C' or $_ eq 'c';
                           $std = '-' if $_ eq 'G' or $_ eq 'g';
                           
                        my $ctx = join '', $ctx1, $ctx2, $ctx3, $ctx4, $ctx5;

                        printf STDOUT "%s\t%d\t%s\t%s\t0.000\t0.00\t0\t0\t0\t0\t1.000e+00\t1.000e+00\n", $scf, $pos, $std, $ctx;
                }
        } @seq_stream;
}
