#!/usr/bin/perl
#Author: Haşim Sak @ Department of Computer Engineering - Boğaziçi University.
#Email: hasim.sak@gmail.com
#Version: 2.0 (This version works with the Boun Morphological Parser output)
#Date: May 27, 2009
#Description: This program implements an averaged perceptron based morphological disambiguation system for Turkish text.
#             You can find the most up to date version at http://www.cmpe.boun.edu.tr/~hasim.
#             For more information and license, you can see readme_license.txt and read the following paper.
#             Haşim Sak, Tunga Güngör, and Murat Saraçlar. Morphological disambiguation of Turkish text with perceptron algorithm.
#             In CICLing 2007, volume LNCS 4394, pages 107-118, 2007.
#             If you want to use this program in your research, please cite this paper.
#             Please note that this implementation is a little bit different than the one described in the paper as explained in the readme_license.txt.
#Important: The input files are expected to be UTF-8 encoded. You can use iconv unix command line tool for encoding conversions.

use strict;
use utf8;
use open ":utf8";
use Net::WebSocket::Server;

$| = 1;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";

my $num_examples;
my %w;
my %avgw;
my %counts;

# INITIALIZATION
srand(792349);
load_model("model.txt");

Net::WebSocket::Server->new(
    listen => 34215,
    on_connect => sub {
        my ($serv, $conn) = @_;
        $conn->on(
            utf8 => sub {
                my ($conn, $msg) = @_;
                my $disamb_text = disamb($msg);
                $conn->send_utf8($disamb_text);
            },
        );
    },
)->start;


sub disamb
{
	my ($amb_text) = @_;

	my @words;
	my @allparses;

	my $result = "";
	my @lines = split /\n/, $amb_text;
	for my $line (@lines)
	{
		chomp($line);
		if ($line =~ /<DOC>/ || $line =~ /<\/DOC>/ || $line =~ /<TITLE>/ || $line =~ /<\/TITLE>/ || $line =~ /<S>/)
		{
			$result .= "$line\n";
			next;
		}
		if ($line =~ /<\/S>/)
		{
			my ($best_score, @best_parse) = best_parse(1, @allparses);
			for (my $i = 0; $i < @words; ++$i)
			{
				$result .= "$words[$i] $best_parse[$i]";
				my @parses = split(/\s+/, $allparses[$i]);
				foreach my $p (@parses)
				{
					if ($p ne $best_parse[$i])
					{
						$result .= " $p";
					}
				}
				$result .= "\n";
			}
			$result .= "$line\n";
			@words = ();
			@allparses = ();
			next;
		}
		my @tokens = split(/\s+/, $line);
		push(@words, shift(@tokens));
		push(@allparses, "@tokens");
	}
	return $result;
}

sub best_parse
{
	my ($averaged_perceptron, @allparses) = @_;
	push(@allparses, "</s>");
	my %bestpath;
	$bestpath{0} = "-1 0 null";
	my $best_state_num = 0;
	my $best_score;
	my %states;
	$states{"<s> <s>"} = 0;
	my $n = 0;
	foreach my $str (@allparses)
	{
		$best_score = -100000;
		my %next_states;
		my @cands = split(/\s+/, $str);
		#shuffle candidates
		for (my $j = 0; $j < @cands; ++$j)
		{
			my $k = rand(@cands);
			my $temp = $cands[$j];
			$cands[$j] = $cands[$k];
			$cands[$k] = $temp;
		}

		foreach my $cand (@cands)
		{
			foreach my $state (keys %states)
			{
				my $state_num = $states{$state};
				my ($prev, $score, $parse) = split(/\s+/, $bestpath{$state_num});

				my @hist = split(/\s+/, $state);
				my @trigram = ($hist[0], $hist[1], $cand);
				my %feat;
				extract_trigram_feat(\%feat, @trigram);
				my $trigram_score;
				if ($averaged_perceptron)
				{
					$trigram_score = ascore(\%feat);
				}
				else
				{
					$trigram_score = score(\%feat);
				}				
				my $new_score = $score + $trigram_score;

				my $new_state = "$hist[1] $cand";
				if (!defined $next_states{$new_state})
				{
					$next_states{$new_state} = ++$n;
				}
				my $next_state_num = $next_states{$new_state};

				if (defined $bestpath{$next_state_num})
				{
					my ($ignore, $cur_score, $ignore) = split(/\s+/, $bestpath{$next_state_num});					
					if ($new_score > $cur_score)
					{
						$bestpath{$next_state_num} = "$state_num $new_score $cand";
					}
				}
				else
				{
					$bestpath{$next_state_num} = "$state_num $new_score $cand";					
				}
				if ($new_score > $best_score)
				{
					$best_score = $new_score;
					$best_state_num = $next_state_num;
				}
			}
		}
		%states = %next_states;
	}

	my @best_parse;
	my $state_num = $best_state_num;
	while ($state_num != 0)
	{
		my ($prev, $score, $parse) = split(/\s+/, $bestpath{$state_num});
		unshift(@best_parse, $parse);
		$state_num = $prev;
	}
	#pop </s>
	pop(@best_parse);
	return ($best_score, @best_parse);
}

sub extract_features
{
	my ($feat_hash, @parse) = @_;

	unshift(@parse, "<s>");
	unshift(@parse, "<s>");
	push(@parse, "</s>");

	my $i;
	for ($i = 2; $i < @parse; ++$i)
	{
		my @trigram = ($parse[$i-2], $parse[$i-1], $parse[$i]);
		extract_trigram_feat($feat_hash, @trigram);
	}
}

sub extract_trigram_feat
{	
	my ($feat_hash, @trigram) = @_;
	my ($w1, $w2, $w3) = @trigram;

	$trigram[0] =~ s/([\+\-][^\[\]]+\[)/ $1/g;
	my ($r1, @IG1) = split(/\s/, $trigram[0]);
	my $IG1 = join("", @IG1);

	$trigram[1] =~ s/([\+\-][^\[\]]+\[)/ $1/g;
	my ($r2, @IG2) = split(/\s/, $trigram[1]);
	my $IG2 = join("", @IG2);

	$trigram[2] =~ s/([\+\-][^\[\]]+\[)/ $1/g;
	my ($r3, @IG3) = split(/\s/, $trigram[2]);
	my $IG3 = join("", @IG3);

	$feat_hash->{"1:$w1 $w2 $w3"}++;
	$feat_hash->{"2:$w1 $w3"}++;
	$feat_hash->{"3:$w2 $w3"}++;
	$feat_hash->{"4:$w3"}++;
	$feat_hash->{"5:$w2 $IG3"}++;
	$feat_hash->{"6:$w1 $IG3"}++;
	$feat_hash->{"7:$r1 $r2 $r3"}++;
	$feat_hash->{"8:$r1 $r3"}++;
	$feat_hash->{"9:$r2 $r3"}++;
	$feat_hash->{"10:$r3"}++;
	$feat_hash->{"11:$IG1 $IG2 $IG3"}++;
	$feat_hash->{"12:$IG1 $IG3"}++;
	$feat_hash->{"13:$IG2 $IG3"}++;
	$feat_hash->{"14:$IG3"}++;
	foreach my $IG (@IG3)
	{
		$feat_hash->{"15:$IG"}++;
	}
	for (my $j = 0; $j < @IG3; ++$j)
	{
		$feat_hash->{"16:$j $IG3[$j]"}++;
	}
	my $len = @IG3;
	$feat_hash->{"17:$len"}++;
}

sub score
{
	my ($feat_hash) = @_;

	my $score = 0;
	foreach my $feat (keys %{$feat_hash})
	{
		$score += $w{$feat} * $feat_hash->{$feat};
	}
	return $score;
}

sub ascore
{
	my ($feat_hash) = @_;

	my $score = 0;
	foreach my $feat (keys %{$feat_hash})
	{
		$score += $avgw{$feat} * $feat_hash->{$feat};
	}
	return $score;
}


sub load_model
{
	my ($model) = @_;
	open(MODEL, $model) || die("cannot open file: $model\n");
	my $line;
	%avgw = ();
	while ($line = <MODEL>)
	{
		chomp($line);
		$line =~ /([^\s]*)\s+(.*)/;
		my $weight = $1;
		my $feat = $2;
		$avgw{$feat} = $weight;
	}
	close(MODEL);
}
