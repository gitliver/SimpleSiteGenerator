#!/bin/bash

#-------------------------------------------------------------------------------
#
#    build.sh
#
#    Build the webpage, copy the static assets, and upload to aws (if requested)
#
#-------------------------------------------------------------------------------

bucket=${1}     # AWS S3 bucket (you can use "x" if you don't have one)
datadir=${2}    # Path to data
outputdir=${3}  # The folder where the output is generated
logfile=${4}    # The file to which logs from jinjagen.py are written
clean=${5}      # If set to "clean", then DELETE EVERYTHING in outputdir (you can use "x" as a placeholder to not clean)
synctoaws=${6}  # If set to "sync", then sync to aws (you can use "x" as a placeholder to not sync)
awsprofile=${7} # AWS profile (you can use "x" as a placeholder if no profile)

echo "********************************************************************************"
echo "* bucket: "${bucket}
echo "* data directory: "${datadir}
echo "* output directory: "${outputdir}
echo "* log file: "${logfile}
echo "* clean directories first? "${clean}
echo "* sync to aws? "${synctoaws}
echo "* aws profile "${awsprofile}
echo "********************************************************************************"
echo

# Get scripts directory
scripts=$( readlink -m $( dirname $0 ) )

mkdir -p ${outputdir}

if [ "${clean}" == "clean" ]; then
    echo "Deleting everything in output directory"
    echo
    # delete these directories, so old stuff doesn't get sync-ed
    rm -r ${outputdir}/*
fi

echo "*** Copy static assets, etc ***"
echo
${scripts}/add_assets.sh ${datadir} ${outputdir} ${scripts}
echo

echo "*** Build webpage ***"
echo
python ${scripts}/jinjagen.py -t ${scripts}/../templates -d ${datadir} -o ${outputdir} --logfile ${logfile}
echo

if [ "${synctoaws}" == "sync" ]; then
    echo "*** Copy to aws ***"
    echo
    ${scripts}/sync.toaws.sh ${outputdir} ${bucket} ${clean} ${awsprofile}
    echo
fi
