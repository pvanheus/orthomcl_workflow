#!/bin/bash

. /etc/profile.d/module.sh
module add orthomcl/orthomcl-2.0.9-stajich
#module add orthomcl/orthomcl-2.0.9
module add mcl
module add blast

MAKECMD="make -f ${MAKEFILE=/cip0/research/projects/seabass/src/seabass/orthomcl/Makefile}"
for var in SKIP_BLAST INPUT BLASTOUT PROJECT ; do 
  # note ${!var} is an indirect variable reference
  # see: http://www.tldp.org/LDP/abs/html/bashver2.html
  # it looks up the variable named by $var
  if [ -n "${!var}" ] ; then
    MAKECMD="$MAKECMD $var=${!var}"
  fi
done
echo "Make command: $MAKECMD"
$MAKECMD
