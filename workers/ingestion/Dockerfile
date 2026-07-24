FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.2
RUN apt-get update && apt-get install -y --no-install-recommends     curl unzip postgresql-client python3 python3-psycopg2 ca-certificates     && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
ENTRYPOINT ["/bin/bash"]
