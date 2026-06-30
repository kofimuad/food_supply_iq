# MinIO object storage, run from a repo Dockerfile so Railway builds it the same
# proven way it builds the api/web services (the prebuilt "Docker Image" source
# path was failing at apply). The official entrypoint prepends `minio` for the
# `server` subcommand, and the exec-form CMD avoids any shell-quoting issues.
FROM minio/minio:latest

EXPOSE 9000 9001

# Data lives on the attached Railway volume mounted at /data.
CMD ["server", "/data", "--console-address", ":9001"]
