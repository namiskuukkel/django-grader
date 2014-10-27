FROM python:3.4
MAINTAINER Riitta Hietaranta <riitta.hietaranta@tut.fi>

# define a mount point
VOLUME /test
WORKDIR /test
ADD to_test.py to_test.py
ADD grade-entrypoint.sh grade-entrypoint.sh
ENTRYPOINT ["/bin/bash", "/test/grade-entrypoint.sh"]