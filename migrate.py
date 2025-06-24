#!/usr/bin/env python3
"""
Database migration management script
"""
import os
import sys
from alembic.config import Config
from alembic import command
import argparse

def get_alembic_config():
    """Get Alembic configuration"""
    alembic_cfg = Config("alembic.ini")
    return alembic_cfg

def upgrade(revision="head"):
    """Upgrade database to specified revision"""
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, revision)
    print(f"Database upgraded to revision: {revision}")

def downgrade(revision):
    """Downgrade database to specified revision"""
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)
    print(f"Database downgraded to revision: {revision}")

def create_migration(message, autogenerate=True):
    """Create a new migration"""
    alembic_cfg = get_alembic_config()
    if autogenerate:
        command.revision(alembic_cfg, message=message, autogenerate=True)
    else:
        command.revision(alembic_cfg, message=message)
    print(f"Created migration: {message}")

def show_history():
    """Show migration history"""
    alembic_cfg = get_alembic_config()
    command.history(alembic_cfg)

def show_current():
    """Show current revision"""
    alembic_cfg = get_alembic_config()
    command.current(alembic_cfg)

def main():
    parser = argparse.ArgumentParser(description="Database migration management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("--revision", default="head", help="Target revision (default: head)")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("message", help="Migration message")
    create_parser.add_argument("--manual", action="store_true", help="Create manual migration (no autogenerate)")
    
    # History command
    subparsers.add_parser("history", help="Show migration history")
    
    # Current command
    subparsers.add_parser("current", help="Show current revision")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "upgrade":
            upgrade(args.revision)
        elif args.command == "downgrade":
            downgrade(args.revision)
        elif args.command == "create":
            create_migration(args.message, autogenerate=not args.manual)
        elif args.command == "history":
            show_history()
        elif args.command == "current":
            show_current()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()