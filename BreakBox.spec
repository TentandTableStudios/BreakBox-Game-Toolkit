# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['C:/Path/To/Your/Project'],  # Change this to your project folder
    binaries=[('C:/Path/To/Python/Lib/site-packages/PIL/.libs/*', 'PIL/.libs')],  # Adjust to your Pillow path
    datas=[
        ('assets/logo.png', 'assets'),
        ('settings.json', '.'),
        ('modding_tool.log', '.')
    ],
    hiddenimports=['PIL._imagingtk'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BreakBox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/logo.ico'
)
