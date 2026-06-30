import { authedFetch } from "./auth";
import type { Media, PresignResponse } from "./types";

/**
 * Upload a photo to a visit: presign -> PUT the bytes straight to storage ->
 * attach the object to the visit. (Offline queueing comes in Epic 7.)
 */
export async function uploadPhoto(
  visitId: string,
  uri: string,
  contentType = "image/jpeg",
): Promise<Media> {
  const presign = await authedFetch<PresignResponse>(`/visits/${visitId}/media/presign`, {
    method: "POST",
    body: JSON.stringify({ content_type: contentType }),
  });

  const blob = await (await fetch(uri)).blob();
  const put = await fetch(presign.upload_url, {
    method: "PUT",
    body: blob,
    headers: { "Content-Type": contentType },
  });
  if (!put.ok) throw new Error(`Upload failed (${put.status})`);

  return authedFetch<Media>(`/visits/${visitId}/media`, {
    method: "POST",
    body: JSON.stringify({ key: presign.key, content_type: contentType }),
  });
}
