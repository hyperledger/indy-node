#!/bin/bash -x

ulogin="$1"
upassword="$2"
uimage="$3"

if [ $# -ne 3 ] ; then
  echo "Incorrect parameters: $0 <user login> <user password> <image to upload>"
  exit 1
fi

docker login -u "$ulogin" -p "$upassword"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Looks like, login was failed. Exit."
  exit 1
fi

docker push "$uimage"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Looks like, image upload was failed. Logout and exit."
  docker logout
  exit 1
fi

echo "Image successfully uploaded"
docker logout
exit "$?"
