"""Alembic environment configuration."""
import sys
import os

# Standard library imports should work
try:
    from pathlib import Path
    from logging.config import fileConfig
    from sqlalchemy import engine_from_config, pool
    from alembic import context
except Exception as e:
    print(f"❌ CRITICAL: Failed to import standard libraries: {e}")
    import traceback
    traceback.print_exc()
    raise

# Add the parent directory to sys.path to ensure app module can be imported
try:
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
except Exception as e:
    print(f"❌ Error manipulating sys.path: {e}")
    raise

# Import app modules with comprehensive error handling
settings = None
Base = None

try:
    from app.config import settings
except ImportError as e:
    print(f"❌ Failed to import app.config: {e}")
    print(f"   Working directory: {os.getcwd()}")
    print(f"   sys.path: {sys.path[:3]}")
    
    app_path = Path(__file__).parent.parent / "app"
    print(f"   app directory exists: {app_path.exists()}")
    if app_path.exists():
        config_path = app_path / "config.py"
        print(f"   config.py exists: {config_path.exists()}")
    
    import traceback
    traceback.print_exc()
    raise
except Exception as e:
    print(f"❌ Error loading app.config settings: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    raise

try:
    # Import Base directly from base.py
    from app.models.base import Base
except ImportError as e:
    print(f"❌ Failed to import Base from app.models.base: {e}")
    import traceback
    traceback.print_exc()
    raise
except Exception as e:
    print(f"❌ Error loading Base: {e}")
    import traceback
    traceback.print_exc()
    raise

# Import models individually with error handling
# Models must be imported for SQLAlchemy to register them with Base.metadata
models_to_import = ['order', 'order_item', 'cart', 'payment', 'shipment', 'saga']
for model_name in models_to_import:
    try:
        __import__(f'app.models.{model_name}')
    except Exception as e:
        print(f"⚠️  Warning: Could not import app.models.{model_name}: {e}")
        # Continue anyway - some models might have dependencies not available during migration

# Alembic Config object
config = context.config

# Get database URL - handle both sync and async formats
try:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Use environment variable if available
        sync_database_url = database_url.replace("+asyncpg", "").replace("postgresql://", "postgresql://")
    else:
        # Fall back to settings
        sync_database_url = settings.database_url.replace("+asyncpg", "")
    
    config.set_main_option("sqlalchemy.url", sync_database_url)
except Exception as e:
    print(f"❌ Error setting database URL: {e}")
    print(f"   DATABASE_URL env: {os.environ.get('DATABASE_URL', 'NOT SET')}")
    raise

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode (SYNC)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
