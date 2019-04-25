ARG PYTHON_VERSION=3.7
FROM python:${PYTHON_VERSION} AS build

# install dependencies
RUN pip install --upgrade pip
COPY requirements*.txt /app/
RUN for reqs in /app/requirements*.txt; do pip install --no-cache-dir -r $reqs; done

# configure and executes build
COPY . /app
WORKDIR /app
RUN echo "Running setup tools..." \
    && python setup.py \
        mypy \
        pylint \
        isort \
        flake8 \
        pytest \
        sdist \
        bdist_wheel \
    && export CI=True \
    && echo "Finished running setup tools..."

# executes code coverage upload to codecov.io
CMD ["/bin/bash", "-c", "bash <(curl -s https://codecov.io/bash)"]



FROM python:${PYTHON_VERSION}-slim AS sample

RUN pip install --upgrade pip

# copy and install dependencies
COPY --from=build /app/samples /samples
COPY --from=build /app/dist /dist
RUN pip install --no-cache-dir /dist/*
RUN pip install --no-cache-dir -r /samples/requirements.txt

# run samples to verify that they work as expected
WORKDIR /samples
RUN bash run_all_samples.sh
ENTRYPOINT ["bash", "run_all_samples.sh"]
