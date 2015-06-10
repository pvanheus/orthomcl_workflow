PROJECT?=nineteen_proteomes
BLASTOUT?=$(PROJECT).blastout
INPUT_DIR?=input
# Don't edit below this line
OUTPUT=$(PROJECT).orthomcl
DB_FILE=$(PROJECT).sqlite
DB_SETTINGS_FILE=$(PROJECT).dbsettings
ORTHOMCL_CONFIG=orthomcl.config
SIM_SEQUENCES=similarSequences.txt
SIMSEQ_LOADED=simseq_loaded
ORTHOMCL_PAIRS_LOG=orthomcl_pairs.log
MCLINPUT=mclInput
MCLOUTPUT=mclOutput

.DELETE_ON_ERROR:

all: $(OUTPUT)

all.fasta: $(INPUT_DIR)
	orthomclFilterFasta $(INPUT_DIR) 10 20 all.fasta poorProteins.fasta

all.fasta.phr: all.fasta
	formatdb -i $< -p T

ifndef SKIP_BLAST
$(BLASTOUT): all.fasta all.fasta.phr 
	blastall -i $< -d $< -o $@ -p blastp -F 'm S' -v 100000 -b 100000 -e 1e-5 -m 8 
else
$(error BLAST will not be run)
endif

$(ORTHOMCL_CONFIG): orthomcl.config.template
	sed "s/DB_FILE/$(DB_FILE)/" $< >$@

$(DB_FILE): $(BLASTOUT) $(ORTHOMCL_CONFIG)
	if [ -f $(DB_FILE) ] ; then rm $(DB_FILE) ; fi
	orthomclInstallSchema orthomcl.config

$(DB_SETTINGS_FILE): $(DB_FILE)
	echo 'pragma temp_store=2;' |sqlite3 $(DB_FILE)
	touch $(DB_SETTINGS_FILE)

$(SIM_SEQUENCES): $(DB_FILE) $(DB_SETTINGS_FILE)
	orthomclBlastParser $(BLASTOUT) $(INPUT_DIR) >$(SIM_SEQUENCES)

$(SIMSEQ_LOADED): $(SIM_SEQUENCES)
	orthomclLoadBlast $(ORTHOMCL_CONFIG) $(SIM_SEQUENCES)
	touch $@

$(ORTHOMCL_PAIRS_LOG): $(SIMSEQ_LOADED)
	orthomclPairs $(ORTHOMCL_CONFIG) $(ORTHOMCL_PAIRS_LOG) cleanup=no

$(MCLINPUT): $(ORTHOMCL_PAIRS_LOG)
	if [ ! -d pairs ] ; then mkdir pairs ; fi
	orthomclDumpPairsFiles $(ORTHOMCL_CONFIG)

$(MCLOUTPUT): $(MCLINPUT)
	mcl $< --abc -I 1.5 -o $@

$(OUTPUT): $(MCLOUTPUT)
	orthomclMclToGroups $(PROJECT) 1 < $< > $@

dbclean:
	rm $(DB_FILE) $(DB_SETTINGS_FILE)
