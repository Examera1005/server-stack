# 1. Patch deezer/utils.py
path = '/usr/local/lib/python3.11/site-packages/deezer/utils.py'
with open(path, 'r') as f:
    code = f.read()

code = code.replace(
    "result['preview'] = track['MEDIA'][0]['HREF']",
    "result['preview'] = track['MEDIA'][0]['HREF'] if track.get('MEDIA') and len(track['MEDIA']) > 0 else None"
)
code = code.replace(
    "result['lyrics_id'] = track['LYRICS_ID']",
    "result['lyrics_id'] = track.get('LYRICS_ID', 0)"
)
code = code.replace(
    "result['physical_release_date'] = track['PHYSICAL_RELEASE_DATE']",
    "result['physical_release_date'] = track.get('PHYSICAL_RELEASE_DATE')"
)
code = code.replace(
    "result['song_contributors'] = track['SNG_CONTRIBUTORS']",
    "result['song_contributors'] = track.get('SNG_CONTRIBUTORS')"
)

with open(path, 'w') as f:
    f.write(code)

# 2. Patch deemix/utils/pathtemplates.py
path_templates = '/usr/local/lib/python3.11/site-packages/deemix/utils/pathtemplates.py'
with open(path_templates, 'r') as f:
    code_t = f.read()

code_t = code_t.replace(
    'filename = filename.replace("%isrc%", track.ISRC)',
    'filename = filename.replace("%isrc%", track.ISRC or "")'
)
code_t = code_t.replace(
    'filename = filename.replace("%upc%", track.album.barcode)',
    'filename = filename.replace("%upc%", track.album.barcode or "")'
)
code_t = code_t.replace(
    'filename = filename.replace("%label%", fixName(track.album.label, c))',
    'filename = filename.replace("%label%", fixName(track.album.label or "", c))'
)
code_t = code_t.replace(
    'filename = filename.replace("%bpm%", str(track.bpm))',
    'filename = filename.replace("%bpm%", str(track.bpm or ""))'
)

with open(path_templates, 'w') as f:
    f.write(code_t)

# 3. Patch deemix/tagger.py
path_tagger = '/usr/local/lib/python3.11/site-packages/deemix/tagger.py'
with open(path_tagger, 'r') as f:
    code_tag = f.read()

code_tag = code_tag.replace(
    "if save['label']:\n        tag.add(TPUB(text=track.album.label))",
    "if save['label'] and track.album.label:\n        tag.add(TPUB(text=track.album.label))"
)
code_tag = code_tag.replace(
    "if save['isrc']:\n        tag.add(TSRC(text=track.ISRC))",
    "if save['isrc'] and track.ISRC:\n        tag.add(TSRC(text=track.ISRC))"
)
code_tag = code_tag.replace(
    "if save['barcode']:\n        tag.add(TXXX(desc=\"BARCODE\", text=track.album.barcode))",
    "if save['barcode'] and track.album.barcode:\n        tag.add(TXXX(desc=\"BARCODE\", text=track.album.barcode))"
)

with open(path_tagger, 'w') as f:
    f.write(code_tag)

print("deezer.utils, pathtemplates, and tagger patched successfully!")
