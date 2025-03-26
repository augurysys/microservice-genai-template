FROM python:3.10.10-slim

RUN apt-get update && apt-get install --reinstall -y build-essential -y git -y libsnappy-dev -y gcc
RUN mkdir -p /src
RUN mkdir -p /src/builds/
#install python requirements
RUN git config --global credential.helper store
ARG GITHUB_TOKEN
RUN echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials \
&& pip install --upgrade pip \
&& rm ~/.git-credentials
ADD requirements.txt /src/
ADD requirements-internal.txt /src/
RUN echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials \
&& pip install -r /src/requirements.txt \
&& rm ~/.git-credentials
RUN echo "https://${GITHUB_TOKEN}:@github.com" >> ~/.git-credentials \
&& pip install -r /src/requirements-internal.txt --no-deps \
&& rm ~/.git-credentials
COPY ./run.sh /
RUN chmod +x /run.sh
# define unprivileged user
RUN addgroup --system app && adduser --system --ingroup app app
ENV PATH=$PATH:~/.local/bin
ENV PYTHONPATH=$PYTHONPATH:/src
RUN chown -R app:app /src
# use the unprivileged user
USER app
# add source code
WORKDIR /src
ADD . /src/

ENTRYPOINT [ "/run.sh" ]
