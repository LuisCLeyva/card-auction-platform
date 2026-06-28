import csv
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from cards.models import Card, CardImage

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"
IMAGES_DIR = FIXTURES_DIR / "images"

STANDARD_COLUMNS = {"card_id", "name", "rarity", "type", "cost", "attribute", "power", "counter", "color", "effect"}


def is_standard_format(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        columns = set(next(csv.reader(f)))
    return STANDARD_COLUMNS.issubset(columns)


def parse_cost_and_life(raw):
    """The catalog stores LEADER life as 'LifeN' and everyone else's mana
    cost as a plain int (or '-' for a few quirky rows)."""
    if raw.startswith("Life"):
        return None, int(raw.removeprefix("Life"))
    if raw.isdigit():
        return int(raw), None
    return None, None


def parse_int(raw):
    return int(raw) if raw.isdigit() else None


class Command(BaseCommand):
    help = "Load all One Piece TCG sets from fixtures/ into the Card catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Card rows before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Card.objects.all().delete()

        media_cards_dir = Path(settings.MEDIA_ROOT) / "cards"
        media_cards_dir.mkdir(parents=True, exist_ok=True)

        csv_files = sorted(p for p in FIXTURES_DIR.glob("*.csv") if is_standard_format(p))
        if not csv_files:
            self.stderr.write(self.style.ERROR(f"No compatible CSV files found in {FIXTURES_DIR}"))
            return

        seen_ids = set()
        total_created, total_updated = 0, 0

        for csv_path in csv_files:
            created, updated = self._seed_file(csv_path, media_cards_dir, seen_ids)
            total_created += created
            total_updated += updated
            self.stdout.write(f"  {csv_path.name}: {created} created, {updated} updated")

        self.stdout.write(self.style.SUCCESS(
            f"Done — {len(csv_files)} sets, {total_created} created, {total_updated} updated."
        ))

    def _seed_file(self, csv_path, media_cards_dir, seen_ids):
        created, updated = 0, 0

        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                card_id = row["card_id"]
                if card_id in seen_ids:
                    continue
                seen_ids.add(card_id)

                cost, life = parse_cost_and_life(row["cost"])
                set_prefix = card_id.split("-")[0].lower()
                images_dir = IMAGES_DIR / set_prefix

                card, was_created = Card.objects.update_or_create(
                    card_id=card_id,
                    defaults={
                        "name": row["name"],
                        "card_type": row["type"],
                        "rarity": row["rarity"],
                        "cost": cost,
                        "life": life,
                        "attribute": row["attribute"] if row["attribute"] != "-" else "",
                        "power": parse_int(row["power"]),
                        "counter": parse_int(row["counter"]),
                        "color": row["color"],
                        "block": row.get("block", ""),
                        "feature": row.get("feature", ""),
                        "effect": row["effect"],
                        "set_name": row["set"],
                    },
                )
                created += was_created
                updated += not was_created

                # Standard image (order=0)
                std_name = self._copy_image(media_cards_dir, images_dir, f"{card_id}.png")
                if std_name:
                    CardImage.objects.update_or_create(
                        card=card, order=0,
                        defaults={"image": std_name, "is_alternate": False},
                    )

                # Alternate arts (_p1, _p2, …) — stop at the first missing file
                for i in range(1, 10):
                    alt_name = self._copy_image(media_cards_dir, images_dir, f"{card_id}_p{i}.png")
                    if not alt_name:
                        break
                    CardImage.objects.update_or_create(
                        card=card, order=i,
                        defaults={"image": alt_name, "is_alternate": True},
                    )

        return created, updated

    @staticmethod
    def _copy_image(media_cards_dir, images_dir, filename):
        src = images_dir / filename
        if not src.exists():
            return ""
        dst = media_cards_dir / filename
        if not dst.exists():
            shutil.copyfile(src, dst)
        return f"cards/{filename}"
