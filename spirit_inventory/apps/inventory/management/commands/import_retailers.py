"""
Import retailers from an XLSX file.

Usage:
    python manage.py import_retailers path/to/retailers.xlsx

Expected columns (case-insensitive, extra columns are ignored):
    License Number   → Retailer.license
    Organization     → Retailer.organization_name
    Store            → Retailer.store_name
    Address          → Retailer.organization_address  (combined with City)
    City             → appended to address as ", {City}, NJ"

Behaviour:
    - Skips rows where License Number is blank.
    - If a retailer with that license already exists → UPDATE (unless --dry-run).
    - If it does not exist → CREATE.
    - Strips all string values before use.
    - Missing Store / Address / City cells are treated as blank (not an error).
    - Prints a summary at the end: created, updated, skipped, errors.

Options:
    --dry-run     Run through the file and report what would happen without
                  writing anything to the database.
    --skip-update Skip rows whose license already exists (create-only mode).
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Import retailers from an XLSX file'

    def add_arguments(self, parser):
        ...
    def handle(self, *args, **options):
        # parse arguments, open file, detect header row, map columns, process rows, print summary ...

        # ── Detect header row ─────────────────────────────────────────────────
        from apps.inventory.models import Retailer
        # ── Process rows ──────────────────────────────────────────────────────

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write('─' * 50)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes were saved.'))
        self.stdout.write(self.style.SUCCESS(f'  Created:  {created}'))
        self.stdout.write(                   f'  Updated:  {updated}')
        self.stdout.write(                   f'  Skipped:  {skipped}')
        if errors:
            self.stdout.write(self.style.ERROR(f'  Errors:   {errors}'))
        else:
            self.stdout.write(               f'  Errors:   {errors}')
        self.stdout.write('─' * 50)