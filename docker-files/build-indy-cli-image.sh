#!/bin/bash -x

# Let this helper script be here. But the main helper should be in special ci repo.

# Get parameter of current git repo to download indy code
function construct_repo_string()
{
  local package_name="$1"
  local curr_branch=$(git rev-parse --abbrev-ref HEAD)
  local curr_commit=$(git rev-parse HEAD)
  local curr_url=$(git config --get remote.origin.url)
  local repo_string="git+$curr_url@$curr_commit#egg=$package_name"
  echo "$repo_string"
}

package_name="indy-client"
repo_string="git+$curr_url@$curr_commit#egg=$package_name"

do_dev_version=0
img_tag="indy-client-pub"
folder='./'

while getopts "dr:f:t:c:" opt; do
  case $opt in
    d)
      do_dev_version=1
      img_tag="indy-client-dev"
      ;;
    r)
      repo_string="$OPTARG"
      ;;
    f)
      client_folder="$OPTARG"
      ;;
    c)
      common_folder="$OPTARG"
      ;;
    t)
      img_tag="$OPTARG"
      ;;
    *)
      echo "Undefined option $opt. Exit"
      exit 1
      ;;
  esac
done

shift $((OPTIND-1))

if [ $do_dev_version -eq 1 ] ; then
  cd "$client_folder" && client_repo_string=$(construct_repo_string "indy_client") ; cd -
  cd "$common_folder" && common_repo_string=$(construct_repo_string "indy_common") ; cd -

  install_indy_client="pip3 install --no-cache-dir -e $client_repo_string"
  install_indy_common="pip3 install --no-cache-dir -e $common_repo_string"
  docker build -t "$img_tag" --build-arg install_indy="$install_indy_cmd" "$folder"
else
  docker build -t "$img_tag" "$folder"
fi
