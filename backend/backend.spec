# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AutoSniper Backend
Packages FastAPI backend into standalone .exe
"""

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include all app files
        ('app', 'app'),
        # Include playwright browsers
        ('C:\\Users\\emin\\AppData\\Local\\ms-playwright', 'ms-playwright'),
        # Include alembic migrations if any
        # ('alembic', 'alembic'),
    ],
    hiddenimports=[
        # FastAPI and dependencies
        'fastapi',
        'fastapi.applications',
        'fastapi.routing',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'fastapi.responses',
        'fastapi.staticfiles',
        'starlette',
        'starlette.applications',
        'starlette.routing',
        'starlette.middleware',
        'starlette.responses',
        'starlette.staticfiles',
        # Pydantic
        'pydantic',
        'pydantic.fields',
        'pydantic_settings',
        # Uvicorn
        'uvicorn',
        'uvicorn.main',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.ext.baked',
        'sqlalchemy.orm',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.postgresql',
        # Other
        'passlib',
        'passlib.handlers',
        'passlib.handlers.bcrypt',
        'jose',
        'jose.jwt',
        'httpx',
        'aiohttp',
        'apscheduler',
        'apscheduler.schedulers',
        'apscheduler.schedulers.asyncio',
        # Playwright
        'playwright',
        'playwright.async_api',
        'playwright._impl._browser',
        'playwright._impl._page',
        'playwright._impl._context',
        # BeautifulSoup
        'bs4',
        'bs4.element',
        'bs4.formatter',
        # Cryptography
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        # App modules
        'app',
        'app.main',
        'app.core',
        'app.api',
        'app.models',
        'app.services',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='autosniper-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console window (backend logs için)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='autosniper-backend',
)
