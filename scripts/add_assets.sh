#!/bin/bash

#-------------------------------------------------------------------------------
#
#    add_assets.sh
#
#    Copy static assets from the data/ to the output/ directory
#
#-------------------------------------------------------------------------------

datadir=${1}	# Data directory
outputdir=${2}	# Output directory
scriptsdir=${3}	# Scripts directory

### Static assets

echo "** Global static assets (css, js, imgs) **"

echo "** Making output directories **"

# Make directories
mkdir -p ${outputdir}/static/css
mkdir -p ${outputdir}/static/js
mkdir -p ${outputdir}/static/img
mkdir -p ${outputdir}/static/video
#mkdir -p ${outputdir}/static/font

echo "** Minify-ing js and css **"

# Uglify (minimize) JS
if [ ! -z "$( ls ${scriptsdir}/../static/js/custom/ )" ]; then
	for i in ${scriptsdir}/../static/js/custom/*.js; do
		echo $i
		myfile=$( basename $i )
		myminfile=$( echo ${myfile} | sed 's|\.js|\.min\.js|' )
		uglifyjs $i --mangle > ${outputdir}/static/js/${myminfile}
	done
fi

# Uglify (minimize) CSS
for i in ${scriptsdir}/../static/css/*.css; do
	echo $i
	myfile=$( basename $i )
	myminfile=$( echo ${myfile} | sed 's|\.css|\.min\.css|' )
	uglifycss $i > ${outputdir}/static/css/${myminfile}
done

# todo: check for files before rsync

# Sync CSS and JS
echo "** Sync-ing js and css **"

if [ ! -z "$( ls ${scriptsdir}/../static/js/vendor/ )" ]; then
	rsync -azv --progress ${scriptsdir}/../static/js/vendor/*.js ${outputdir}/static/js/
else
	echo "${scriptsdir}/../static/js/vendor/ empty"
fi

# Images for core website
if [ ! -z "$( ls ${datadir}/static/img/ )" ]; then
	rsync -azv --progress ${datadir}/static/img/* ${outputdir}/static/img/
else
	echo "${datadir}/static/img empty"
fi

# Font
#rsync -azv --progress --exclude notes ${datadir}/static/font/* ${outputdir}/static/font/

# Posts
echo "** Sync-ing static assets of visual posts **"
if [ ! -z "$( ls ${datadir}/published/img/ )" ]; then
	rsync -az --progress ${datadir}/published/img/* ${outputdir}/static/img/
else
	echo "${datadir}/published/img/ empty"
fi
if [ ! -z "$( ls ${datadir}/published/video/ )" ]; then
	rsync -az --progress ${datadir}/published/video/* ${outputdir}/static/video/
else
	echo "${datadir}/published/img/ empty"
fi

echo "** Sync-ing static assets of article posts **"
rsync -az --progress ${datadir}/published/article/*/img/* ${outputdir}/static/img/
rsync -az --progress ${datadir}/published/article/*/video/* ${outputdir}/static/video/
