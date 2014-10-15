
FROM python:3.4
MAINTAINER Riitta Hietaranta <riitta.hietaranta@tut.fi>

# define a mount point
VOLUME /test
WORKDIR /test
ADD entrypoint.sh /test/entrypoint.sh
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]