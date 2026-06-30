import { authedFetch } from "./auth";
import type { Sample, SampleCreate } from "./types";

export function recordSample(accountId: string, body: SampleCreate): Promise<Sample> {
  return authedFetch<Sample>(`/accounts/${accountId}/samples`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
