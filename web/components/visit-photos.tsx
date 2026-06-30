"use client";

import { useVisitMedia } from "@/lib/use-media";

/** Thumbnail strip for a visit's photos (Story 3.3). */
export function VisitPhotos({ visitId }: { visitId: string }) {
  const { data } = useVisitMedia(visitId);
  if (!data || data.length === 0) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {data.map((m) => (
        // eslint-disable-next-line @next/next/no-img-element -- presigned external URL
        <a key={m.id} href={m.view_url} target="_blank" rel="noreferrer">
          <img
            src={m.view_url}
            alt="visit photo"
            className="h-16 w-16 rounded-md border object-cover"
          />
        </a>
      ))}
    </div>
  );
}
