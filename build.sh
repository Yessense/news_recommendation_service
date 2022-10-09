docker build . \
    -f Dockerfile \
    --build-arg UID=${UID} \
    --build-arg GID=${UID} \
    -t segmentator:latest
