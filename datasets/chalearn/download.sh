#!/bin/sh

URL="http://www.causality.inf.ethz.ch/AutoML/"
FILES="adult.zip cadata.zip digits.zip dorothea.zip newsgroups.zip"
VALID="http://www.causality.inf.ethz.ch/AutoML/phase0_valid.zip"

# Download challenge files
for f in $FILES; do
    name=`echo ${f} | sed -E 's;(.*)\.zip;\1;'`
    curl "${URL}${f}" -o /tmp/${f}
    unzip /tmp/${f} -d "./${name}"
done

# Download solutions
rm -rf /tmp/valid-data/
curl "${VALID}" -o /tmp/valid.zip
unzip /tmp/valid.zip -d /tmp/valid-data/

for f in `ls /tmp/valid-data/`; do
    name=`echo "${f}" | sed -E 's;(.*)_.*;\1;'`
    mv "/tmp/valid-data/${f}" "./${name}/"
done

# Build original dataset
rm -f ./*/*_test.data

for f in $FILES; do
    name=`echo ${f} | sed -E 's;(.*)\.zip;\1;'`
    cat ./${name}/${name}_*.data > ./${name}/${name}.data
    cat ./${name}/${name}_*.solution > ./${name}/${name}.solution
done


