#!/bin/bash
/usr/local/bin/salt 'node*' cmd.run 'ipmitool sel list' | mail -s "Weekly Hypervisor SEL report" infra@boinc.com 
