#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
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
