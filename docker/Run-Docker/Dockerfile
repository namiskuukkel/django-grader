
FROM python:3.4
MAINTAINER Riitta Hietaranta <riitta.hietaranta@tut.fi>

# define a mount point
VOLUME /test
WORKDIR /test
ADD to_test.py to_test.py
ENTRYPOINT python3.4 /test/to_test.py
