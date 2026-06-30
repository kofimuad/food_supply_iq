# MinIO on Railway (repo-Dockerfile path)

The prebuilt "Docker Image" source for `minio/minio` was failing to deploy on
Railway at the apply step. This builds MinIO from a Dockerfile instead — the same
mechanism the `api` and `web` services use successfully.

## Set up the Railway service
1. **+ New → GitHub Repo** → `kofimuad/food_supply_iq`.
2. The new service → **Settings**:
   - **Root Directory** = `infra/minio`  (Railway auto-detects this Dockerfile)
   - Rename the service to **`minio`**.
3. **Variables** (strong values; password ≥ 8 chars, user ≥ 3):
   ```
   MINIO_ROOT_USER     = fsiqadmin
   MINIO_ROOT_PASSWORD = <python -c "import secrets; print(secrets.token_urlsafe(32))">
   ```
4. **Attach a Volume** mounted at `/data`.
5. Deploy. Once it's **online**, go to **Settings → Networking → Public** and
   **Generate Domain** with **target port 9000** (the S3 API).

## Wire the API service
On the `api` service → Variables (plain strings — not `${{...}}` references):
```
S3_ENDPOINT           = https://<minio public domain from step 5>
S3_ACCESS_KEY         = <MINIO_ROOT_USER>
S3_SECRET_KEY         = <MINIO_ROOT_PASSWORD>
S3_BUCKET             = fsiq-media
S3_REGION             = us-east-1
S3_AUTO_CREATE_BUCKET = true
```
Redeploy `api`. Verify with `POST /visits/{id}/media/presign` in `/docs`, then
attach a photo from the mobile app.
