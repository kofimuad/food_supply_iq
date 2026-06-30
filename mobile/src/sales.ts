import { authedFetch } from "./auth";
import type { Order, OrderCreate, Sample, SampleCreate } from "./types";

export function recordSample(accountId: string, body: SampleCreate): Promise<Sample> {
  return authedFetch<Sample>(`/accounts/${accountId}/samples`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function createOrder(accountId: string, body: OrderCreate): Promise<Order> {
  return authedFetch<Order>(`/accounts/${accountId}/orders`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
