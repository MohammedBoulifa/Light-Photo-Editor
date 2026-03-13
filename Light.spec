# Light - Photo Editor PyInstaller Spec File
# Run with: pyinstaller Light.spec
# All The Rights to The Creator: Mohammed Boulifa

block_cipher = None

a = Analysis(
    ['Light.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Icon.png', '.'),   # App icon used by root.iconphoto()
    ],
    hiddenimports=[
        # tkinter
        'tkinter',
        'tkinter.filedialog',
        # Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageFilter',
        'PIL.ImageEnhance',
        'PIL.ImageOps',
        'PIL._tkinter_finder',
        'PIL.PngImagePlugin',
        'PIL.JpegImagePlugin',
        'PIL.BmpImagePlugin',
        'PIL.GifImagePlugin',
        'PIL.WebPImagePlugin',
        'PIL.PdfImagePlugin',
        # numpy
        'numpy',
        # ctypes (Windows dark-mode / DWM)
        'ctypes',
        'ctypes.wintypes',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Light - Photo Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Icon.png',                # App icon (matches root.iconphoto in Light.py)
)
