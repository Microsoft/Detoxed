ARG PYTHON_VERSION=3.7

FROM python:${PYTHON_VERSION} AS build

RUN pip install --upgrade pip
COPY requirements*.txt /app/
RUN for reqs in /app/requirements*.txt; do pip install --no-cache-dir -r $reqs; done

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
    && echo "Finished running setup tools..."

FROM python:${PYTHON_VERSION}-slim AS samples
COPY --from=build /app/samples /samples
COPY --from=build /app/dist /dist
RUN pip install --no-cache-dir /dist/*

# run the samples to verify that they do not fail
RUN python -m samples
ENTRYPOINT ["python", "-m", "samples"]
