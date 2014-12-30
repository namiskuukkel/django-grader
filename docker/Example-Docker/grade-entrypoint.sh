prog=$1
uid=$2
if [ -z $1 ]; then
echo "you must provide a file"
exit 1
fi
if [ -z $uid ]; then
uid=10000
fi

groupadd code
useradd student -G code -d "/home/grader" -m grader
chgrp code /home/grader
chmod 0775 /home/grader
cd /home/grader
chroot /home/grader
su - student