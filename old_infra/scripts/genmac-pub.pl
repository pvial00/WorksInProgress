#!/usr/bin/perl
open FILE, "/home/vm/pubmac.index" or die $!;
read FILE, $smac, 17;
close FILE;
open FILE2, ">/home/vm/pubmac.index" or die $!;
my $mac_str = $smac;

( my $mac_hex = $mac_str ) =~ s/://g;
my ($mac_hi, $mac_lo) = unpack("nN", pack('H*', $mac_hex));

if ($mac_lo == 0xFFFFFFFF) {
	    $mac_hi = ($mac_hi + 1) & 0xFFFF;
	        $mac_lo = 0;
	} else {
		    ++$mac_lo;
	    }

	    $mac_hex = sprintf("%04X%08X", $mac_hi, $mac_lo);
	    $mac_str = join(':', $mac_hex =~ /../sg);
	    printf $mac_str;
	    print FILE2 $mac_str;
	    close FILE2;
