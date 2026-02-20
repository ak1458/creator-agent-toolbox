import re

with open('backend/app/core/config.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''
    @field_validator("database_url", "checkpoint_db_url", mode="before")
    @classmethod
    def _ensure_async_sqlite(cls, value):
        if not value: return value
        v = str(value)
        if v.startswith("sqlite:///"): return v.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        if not v.startswith(("sqlite", "postgresql")):
            c = v.lstrip("./")
            return f"sqlite+aiosqlite://{c}" if c.startswith("/") else f"sqlite+aiosqlite:///{c}"
        return v

    @field_validator("debug", mode="before")'''

if "_ensure_async_sqlite" not in text:
    text = text.replace('    @field_validator("debug", mode="before")', replacement)
    with open('backend/app/core/config.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patch applied")
else:
    print("Already patched")
