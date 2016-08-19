#!/bin/sh

URL_1="http://www.causality.inf.ethz.ch/AutoML/"
FILES_1="adult.zip cadata.zip digits.zip dorothea.zip newsgroups.zip christine.zip jasmine.zip philippine.zip madeline.zip sylvine.zip albert.zip dilbert.zip fabert.zip robert.zip volkert.zip alexis.zip dionis.zip grigoris.zip jannis.zip wallis.zip"

for f in $FILES_1; do
    name=`echo ${f} | sed -E 's;(.*)\.zip;\1;'`
    curl "${URL_1}${f}" -o /tmp/${f}
    unzip /tmp/${f} -d ./${name}
done

