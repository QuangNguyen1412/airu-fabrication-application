# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
#             pathex=['C:\\Python\\Python37\\Lib\\site-packages'],
             binaries=[],
             datas=[('credential/scottgale-bigquery-secret.json', 'credential/.'),
             ('scripts/DYMO/PrintLabel.exe', 'scripts/DYMO/.'),
             ('resources/label/Small.label', 'resources/label/.'),
             ('resources/binary/ota_data_initial.bin', 'resources/binary/.'),
             ('resources/binary/bootloader.bin', 'resources/binary/.'),
             ('resources/binary/airu-firmware-2.0.bin', 'resources/binary/.'),
             ('resources/binary/partitions_two_ota.bin', 'resources/binary/.'),
             ('scripts/esptool.py', 'scripts/.'),
             ('AIRU.png', '.'),
             ('README.md', '.')],
             hiddenimports=[],
             hookspath=['C:\\Users\\lnis\\Desktop\\qang\\flash_gui\\pyinstaller_hook'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='fabrication-app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='fabrication-app')
