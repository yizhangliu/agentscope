#!/bin/bash

set -e

# Generate the API rst files
<<<<<<< HEAD
sphinx-apidoc -o source/build_api ../../../src/agentscope -t source/_templates -e

# Build the html
sphinx-build -M html source build
=======
sphinx-apidoc -o api ../../../src/agentscope -t ../_templates -e

# Build the html
sphinx-build -M html ./ build
>>>>>>> 6ee8fa352bcaf888adf82124e0e0a5c394454506
