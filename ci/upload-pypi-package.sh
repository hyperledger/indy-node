#!/bin/bash -x

if [ "$1" = "--help" ] ; then
  echo "Usage: $0 <path-to-repo-folder>"
fi

cdir=`pwd`
repo="$1"

cd $repo 

echo -e "\n\nAbout to start uploading from cur dir: $(pwd)"

python3 setup.py register -r pypitest
ret=$?
if [ $ret -ne 0 ] ; then
  echo "FAILED ret: $ret"
  exit $ret
fi

python3 setup.py sdist upload -r pypitest
ret=$?
if [ $ret -ne 0 ] ; then
  echo "FAILED ret: $ret"
  exit $ret
fi

echo -e "About to upload to pypi..."
python3 setup.py register -r pypi
ret=$?
if [ $ret -ne 0 ] ; then
  echo "FAILED ret: $ret"
  exit $ret
fi

python3 setup.py sdist upload -r pypi
ret=$?
if [ $ret -ne 0 ] ; then
  echo "FAILED ret: $ret"
  exit $ret
fi

echo -e "finished uploading $repoName to pypi\n"
