#!/usr/bin/env perl


use strict;
use warnings;


my %box;

open SUB, '<',           "$ARGV[0]" or die "$!\n" if $ARGV[0] !~ m/\.gz$/;
open SUB, '-|', "gzip -cd $ARGV[0]" or die "$!\n" if $ARGV[0] =~ m/\.gz$/;
while (<SUB>)
{
        next if m/^#/ or m/context/; chomp;

        my @line = split /\t/;
        $box{$line[0]}{$line[1]} = join "\t", @line[4..11];
}
close SUB;

while (<STDIN>)
{
        next if m/^#/ or m/context/; chomp;

        my @line = split /\t/;
        if (defined $box{$line[0]}{$line[1]})
        {
                printf STDOUT "%s\t", join "\t", @line[0..3];
                printf STDOUT "%s\n", $box{$line[0]}{$line[1]};

                delete $box{$line[0]}{$line[1]};
        }
        else
        {
                printf STDOUT "%s\n", join "\t", @line;
        }
}
