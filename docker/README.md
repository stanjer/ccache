Some more docker builds, more like Travis CI.

precise: (Ubuntu 12.04 LTS)
- gcc
- clang

trusty: (Ubuntu 14.04 LTS)
- gcc-7
- mingw

xenial: (Ubuntu 16.04 LTS)
- default

Build with: `docker build -f Dockerfile.* ..`
