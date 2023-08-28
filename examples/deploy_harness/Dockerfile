FROM dtch1997/ml-ubuntu-cuda:ubuntu-20.04-python3.9-latest

COPY ./requirements /tmp/requirements
RUN python3 -m pip --no-cache-dir install -U pip wheel setuptools \
    && python3 -m pip --no-cache-dir install -r /tmp/requirements/base.txt \
    && rm -r /tmp/requirements

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
USER $USERNAME
