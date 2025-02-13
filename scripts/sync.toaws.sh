#!/bin/bash

#-------------------------------------------------------------------------------
#
#    sync.toaws.sh
#
#    Sync files to AWS S3 bucket
#
#-------------------------------------------------------------------------------

outputdir=${1}  # Local site directory
bucket=${2}     # AWS bucket name
clean=${3}      # If set to "clean", remove stuff in bucket
awsprofile=${4} # AWS profile

if [ "${clean}" == "clean" ]; then
    echo "** Clean s3 buckets **"
    aws s3 rm --profile ${awsprofile} --recursive s3://${bucket}/post/
    aws s3 rm --profile ${awsprofile} --recursive s3://${bucket}/static/
fi

echo "** Copy index.html error.html **"
aws s3 cp --profile ${awsprofile} ${outputdir}/index.html s3://${bucket}/
aws s3 cp --profile ${awsprofile} ${outputdir}/error.html s3://${bucket}/

echo "** Copy static folder **"
# css, js, img files
aws s3 sync --profile ${awsprofile} ${outputdir}/static s3://${bucket}/static/

echo "** Copy posts **"
aws s3 sync --profile ${awsprofile} ${outputdir}/post s3://${bucket}/article/
