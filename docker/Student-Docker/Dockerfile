FROM python:3.4
MAINTAINER Riitta Hietaranta <riitta.hietaranta@tut.fi>

# define a mount point
VOLUME /test/
ADD student_code.py /test/student_code.py
WORKDIR /test/
ENTRYPOINT python3.4 student_code.py
