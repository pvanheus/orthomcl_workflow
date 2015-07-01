### OrthoMCL procedure

Firstly we use the [Stajich Lab OrthoMCL](https://github.com/stajichlab/OrthoMCL).

Also see the OrthoMCL [user guide](http://orthomcl.org/common/downloads/software/v2.0/UserGuide.txt) and the
OrthoMCL [algorithm guide](https://docs.google.com/document/d/1RB-SqCjBmcpNq-YbOYdFxotHGuU7RK_wqxqDAMjyP_w/pub). 

### Processing FASTA files for OrthoMCL

Use orthomclAdjustFasta to convert each FASTA file of proteins to the format expected by orthoMCL. This script
expects IDs to be unique and delimited with spaces or | characters. Command is:

    orthomclAdjustFasta <prefix> <FASTA filename> <field number>

So for e.g. seabass proteins where the ID is in the first field (e.g. `>contig1_g1 Contig1 first gene`) in a
file called `sbt_prots.fasta` where you want the prefix sbt use:

    orthomclAdjustFasta sbt sbt_prots.fasta 1

This makes a file named `<prefix>.fasta` e.g. `sbt.fasta`.

### Makefile for OrthoMCL

The `Makefile` does all steps necessary for OrthoMCL, from creating the input FASTA file from previously
formatted inputs to running the all-vs-all BLAST to running the different OrthoMCL programs. It can be run
using the `run_orthomcl_make.sh` script. The all-vs-all BLAST step is the most time-consuming steps of
the OrthoMCL run. If this has already been run, and you want to force skipping BLAST, set the SKIP\_BLAST 
variable to some value. E.g.:

    $ qsub -S /bin/bash -v SKIP_BLAST=1 -q all.q -cwd run_orthomcl_make.sh

Note the use of `-S /bin/bash` to force `bash` to be used to interpret the script. Otherwise
`sh` might be used and errors will result.

The `Makefile` uses three variables that can be set from the environment:

* INPUT for the directory containing input FASTA files

* PROJECT for the name of the project. Each OrthoMCL run should have a unique project name.

* BLASTOUT for the name of the file to store all-vs-all BLAST output in. Default is <PROJECT>.blastout

These can be set and passed to `qsub` with the `-v` flag as illustrated above. E.g.

    $ qsub -S /bin/bash -v PROJECT=fish_vs_seal -q all.q -cwd run_orthomcl_make.sh

By default the `run_orthomcl_make.sh` script uses the `Makefile` in `/cip0/research/projects/seabass/src/seabass/orthomcl` but
this can be changed by setting the `MAKEFILE` environment variable.

### Dependencies

These need to be in your path. In the `run_orthomcl_make.sh` script they are added to the path using
(SANBI specific) environment modules, but non-SANBI users will need to add them to the PATH themselves.

* [MCL](http://www.micans.org/mcl/sec_description1.html)
* The Stajich version of [OrthoMCL](http://www.micans.org/mcl/sec_description1.html)
* Legacy [BLAST](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/release/LATEST/)

### TODO

* Incorporate [FastOrtho](http://enews.patricbrc.org/fastortho/).
