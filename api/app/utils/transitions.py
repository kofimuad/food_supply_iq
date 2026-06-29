"""Allowed account pipeline status transitions (Story 1.4)."""

from app.models.enums import AccountStatus as S

# Funnel: lead → in_discussion → sampled → trial → repeat, with not_interested
# reachable from anywhere and re-engagement back out of it.
ALLOWED_TRANSITIONS: dict[S, set[S]] = {
    S.lead: {S.in_discussion, S.sampled, S.not_interested},
    S.in_discussion: {S.sampled, S.trial, S.not_interested, S.lead},
    S.sampled: {S.trial, S.not_interested, S.in_discussion},
    S.trial: {S.repeat, S.not_interested, S.sampled},
    S.repeat: {S.not_interested, S.trial},
    S.not_interested: {S.lead, S.in_discussion},
}


def allowed_next(current: S) -> set[S]:
    return ALLOWED_TRANSITIONS.get(current, set())


def can_transition(current: S, target: S) -> bool:
    return target in allowed_next(current)
