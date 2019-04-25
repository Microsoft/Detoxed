#!/usr/bin/env bash

set -euo pipefail

# run CLI based examples
(cd ./samplecli && bash run.sh)

# run Python based examples
(python -m samplepy)

echo "All samples ran successfully!"
