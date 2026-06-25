"""Seed demo data for local development / testing.

Creates a manager, two reps, a product catalog, and demo accounts in the DMV
(Washington DC metro) and Accra, plus one full sample -> trial -> repeat chain
so the funnel and relationships are exercisable end-to-end.

Run with:  python -m app.seed   (idempotent — no-ops if users already exist)
"""

import asyncio
from datetime import UTC, datetime, timedelta

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import (
    Account,
    Contact,
    Order,
    OrderItem,
    Product,
    Sample,
    SampleItem,
    User,
    Visit,
)
from app.models.enums import (
    AccountCategory,
    AccountStatus,
    OrderType,
    UserRole,
    VisitOutcome,
)


def point(lng: float, lat: float) -> WKTElement:
    """geography(Point, 4326) literal — note PostGIS order is (lng, lat)."""
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


async def seed() -> None:
    async with SessionLocal() as db:
        existing = await db.scalar(select(func.count()).select_from(User))
        if existing:
            print(f"Seed skipped — {existing} users already present.")
            return

        # --- Users ---
        manager = User(
            email="manager@foodsupplyiq.test",
            full_name="Bismark Agyei",
            role=UserRole.manager,
        )
        rep_dmv = User(
            email="rep.dmv@foodsupplyiq.test", full_name="Ama Boateng", role=UserRole.rep
        )
        rep_accra = User(
            email="rep.accra@foodsupplyiq.test", full_name="Kwesi Mensah", role=UserRole.rep
        )
        db.add_all([manager, rep_dmv, rep_accra])
        await db.flush()

        # --- Products (African food staples) ---
        products = [
            Product(name="Jollof Rice Mix", pack_size="500g", price="4.50", currency="USD"),
            Product(name="Red Palm Oil", pack_size="1L", price="9.00", currency="USD"),
            Product(name="Garri (cassava)", pack_size="5kg", price="12.00", currency="USD"),
            Product(name="Egusi Seeds", pack_size="1kg", price="14.00", currency="USD"),
            Product(name="Plantain Chips", pack_size="200g", price="2.25", currency="USD"),
            Product(name="Shito Pepper Sauce", pack_size="350g", price="6.50", currency="USD"),
        ]
        db.add_all(products)
        await db.flush()

        # --- Accounts: DMV (Washington DC metro) ---
        dmv_accounts = [
            Account(
                name="Adams Morgan African Market",
                category=AccountCategory.grocery_store,
                status=AccountStatus.repeat,
                address="1800 Columbia Rd NW, Washington, DC 20009",
                location=point(-77.0421, 38.9213),
                assigned_rep_id=rep_dmv.id,
            ),
            Account(
                name="Silver Spring Halal & African Foods",
                category=AccountCategory.wholesaler,
                status=AccountStatus.trial,
                address="8208 Fenton St, Silver Spring, MD 20910",
                location=point(-77.0260, 38.9959),
                assigned_rep_id=rep_dmv.id,
            ),
            Account(
                name="Takoma African & Caribbean Grocery",
                category=AccountCategory.grocery_store,
                status=AccountStatus.sampled,
                address="6925 Laurel Ave, Takoma Park, MD 20912",
                location=point(-77.0172, 38.9779),
                assigned_rep_id=rep_dmv.id,
            ),
            Account(
                name="Alexandria West African Caterers",
                category=AccountCategory.caterer,
                status=AccountStatus.lead,
                address="5701 Duke St, Alexandria, VA 22304",
                location=point(-77.1290, 38.8127),
                assigned_rep_id=rep_dmv.id,
            ),
        ]

        # --- Accounts: Accra ---
        accra_accounts = [
            Account(
                name="Makola Market Wholesale",
                category=AccountCategory.wholesaler,
                status=AccountStatus.repeat,
                address="Kojo Thompson Rd, Accra",
                location=point(-0.2010, 5.5470),
                assigned_rep_id=rep_accra.id,
            ),
            Account(
                name="Osu Food Mart",
                category=AccountCategory.grocery_store,
                status=AccountStatus.in_discussion,
                address="Oxford St, Osu, Accra",
                location=point(-0.1820, 5.5570),
                assigned_rep_id=rep_accra.id,
            ),
            Account(
                name="East Legon Restaurant Supply",
                category=AccountCategory.restaurant,
                status=AccountStatus.trial,
                address="Lagos Ave, East Legon, Accra",
                location=point(-0.1620, 5.6360),
                assigned_rep_id=rep_accra.id,
            ),
        ]
        db.add_all(dmv_accounts + accra_accounts)
        await db.flush()

        # --- Contacts ---
        db.add_all(
            [
                Contact(
                    account_id=dmv_accounts[0].id,
                    name="Grace Owusu",
                    role="Owner",
                    phone="+1 202-555-0142",
                    is_primary=True,
                ),
                Contact(
                    account_id=accra_accounts[0].id,
                    name="Yaw Darko",
                    role="Purchasing Manager",
                    phone="+233 24 555 0188",
                    is_primary=True,
                ),
            ]
        )

        # --- Full sample -> trial -> repeat chain on the DMV repeat account ---
        anchor = dmv_accounts[0]
        now = datetime.now(UTC)

        visit = Visit(
            account_id=anchor.id,
            rep_id=rep_dmv.id,
            location=point(-77.0421, 38.9213),
            occurred_at=now - timedelta(days=40),
            outcome=VisitOutcome.sample_given,
            notes="Dropped Jollof mix + palm oil samples; owner keen.",
        )
        db.add(visit)
        await db.flush()

        sample = Sample(
            account_id=anchor.id,
            rep_id=rep_dmv.id,
            visit_id=visit.id,
            occurred_at=now - timedelta(days=40),
        )
        sample.items = [
            SampleItem(product_id=products[0].id, quantity=2),
            SampleItem(product_id=products[1].id, quantity=1),
        ]
        db.add(sample)
        await db.flush()

        trial = Order(
            account_id=anchor.id,
            rep_id=rep_dmv.id,
            order_type=OrderType.trial,
            sample_id=sample.id,
            occurred_at=now - timedelta(days=28),
            total_value="54.00",
            currency="USD",
        )
        trial.items = [
            OrderItem(product_id=products[0].id, quantity=12, unit_price="4.50"),
        ]
        repeat = Order(
            account_id=anchor.id,
            rep_id=rep_dmv.id,
            order_type=OrderType.repeat,
            occurred_at=now - timedelta(days=7),
            total_value="90.00",
            currency="USD",
        )
        repeat.items = [
            OrderItem(product_id=products[0].id, quantity=12, unit_price="4.50"),
            OrderItem(product_id=products[1].id, quantity=4, unit_price="9.00"),
        ]
        db.add_all([trial, repeat])

        await db.commit()

        print(
            "Seeded: 3 users, "
            f"{len(products)} products, "
            f"{len(dmv_accounts) + len(accra_accounts)} accounts, "
            "2 contacts, 1 visit, 1 sample, 2 orders (1 trial + 1 repeat)."
        )


if __name__ == "__main__":
    asyncio.run(seed())
