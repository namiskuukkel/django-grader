FROM python:3.4
MAINTAINER Riitta Hietaranta <riitta.hietaranta@tut.fi>

# define a mount point
ADD to_test.py /test/to_test.py
WORKDIR /test
ENTRYPOINT python3.4 /test/to_test.py