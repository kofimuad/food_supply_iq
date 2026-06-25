"""Enumerations used across the domain model."""

import enum


class UserRole(enum.StrEnum):
    manager = "manager"
    rep = "rep"


class AccountCategory(enum.StrEnum):
    grocery_store = "grocery_store"
    wholesaler = "wholesaler"
    restaurant = "restaurant"
    caterer = "caterer"
    vendor = "vendor"


class AccountStatus(enum.StrEnum):
    """Sample → Trial → Repeat funnel stages (Epic 4)."""

    lead = "lead"
    in_discussion = "in_discussion"
    sampled = "sampled"
    trial = "trial"
    repeat = "repeat"
    not_interested = "not_interested"


class VisitOutcome(enum.StrEnum):
    no_contact = "no_contact"
    interested = "interested"
    not_interested = "not_interested"
    sample_given = "sample_given"
    order_placed = "order_placed"
    follow_up_needed = "follow_up_needed"


class OrderType(enum.StrEnum):
    trial = "trial"
    repeat = "repeat"
