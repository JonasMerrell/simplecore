# Replace the Goliath hotend body ("LSD Air cooled_1", body 1:8 of the "Purchased parts" studio)
# with the official VzBoT Goliath air-cooled STEP (github.com/VzBoT3D/Goliath, CAD/Goliath Mockup AIR.STEP).
# The body converted from the Onshape .x_t had its big heater-core cone as one closed face with no seam,
# which rCAD's mesher can't triangulate, so the hotend showed with no core (heatsink and nozzle floating).
# The official STEP is the same solid (same volume and bounding box) with the cone split in two faces.
#
# usage: get purchased.stp from the studio: zlib.decompress(base64.b64decode(op['data'])) of its import feature
#        rcad script rebuild.rhai .   (in a folder with purchased.stp and gol-air.step; writes purchased-new.stp)
#        python3 splice_goliath.py purchased-new.stp X-carriage.json [more.json ...]   (edits in place)
import base64, json, sys, zlib
new = open(sys.argv[1], 'rb').read()
data = base64.b64encode(zlib.compress(new, 9)).decode()
for path in sys.argv[2:]:
    d = json.load(open(path))
    st = [s for s in d['studios'] if s['name'] == 'Purchased parts']
    assert len(st) == 1, path
    doc = st[0]['doc']
    assert doc['parts']['1:8']['name'] == 'LSD Air cooled_1', path
    op = doc['features'][0]['op']
    assert op['type'] == 'import' and op['format'] == 'step'
    op['data'] = data
    json.dump(d, open(path, 'w'))
    print(path, 'ok')
