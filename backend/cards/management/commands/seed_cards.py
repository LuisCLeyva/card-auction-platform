import csv
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from cards.models import Card

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"
CSV_PATH = FIXTURES_DIR / "op01.csv"
IMAGES_DIR = FIXTURES_DIR / "images" / "op01"


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
    help = "Load the One Piece TCG -ROMANCE DAWN- [OP01] set into the Card catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Card rows before seeding.",
        )

    def handle(self, *args, **options):
        if not CSV_PATH.exists():
            self.stderr.write(self.style.ERROR(f"Missing fixture: {CSV_PATH}"))
            return

        if options["clear"]:
            Card.objects.all().delete()

        media_cards_dir = Path(settings.MEDIA_ROOT) / "cards"
        media_cards_dir.mkdir(parents=True, exist_ok=True)

        seen_ids = set()
        created, updated = 0, 0

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                card_id = row["card_id"]
                if card_id in seen_ids:
                    continue  # the catalog repeats a row per alt-art image
                seen_ids.add(card_id)

                cost, life = parse_cost_and_life(row["cost"])
                image_name = self._copy_image(media_cards_dir, f"{card_id}.png")
                alt_image_name = self._copy_image(media_cards_dir, f"{card_id}_p1.png")

                _, was_created = Card.objects.update_or_create(
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
                        "block": row["block"],
                        "feature": row["feature"],
                        "effect": row["effect"],
                        "set_name": row["set"],
                        "image": image_name,
                        "alt_image": alt_image_name,
                    },
                )
                created += was_created
                updated += not was_created

        self.stdout.write(self.style.SUCCESS(f"Seeded cards: {created} created, {updated} updated."))

    @staticmethod
    def _copy_image(media_cards_dir, filename):
        src = IMAGES_DIR / filename
        if not src.exists():
            return ""
        dst = media_cards_dir / filename
        if not dst.exists():
            shutil.copyfile(src, dst)
        return f"cards/{filename}"
