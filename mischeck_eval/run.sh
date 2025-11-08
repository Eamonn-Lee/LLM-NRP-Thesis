#!/bin/bash

#Laziest pipe

COMMONS_CLI="commons-cli-1.3.1.jar"
JSON_JAR="json-20230227.jar"

# Compilation
javac -cp "$COMMONS_CLI:$JSON_JAR" *.java  data/*

# Command
#java -jar Solver.jar --summary -s n005w4 -w 1,2,3,3 -h 0 -sol
SCE="$1"
WK="$2"
H="$3"
CSOL="$4"

SOL_ARG="-s ${SCE} -w ${WK} -h ${H} -csol ${CSOL} -sol --printConflicts"

# Run with the same classpath
java -cp ".:$COMMONS_CLI:$JSON_JAR" Eval $SOL_ARG

#clean class files
rm *.class
rm data/*.class