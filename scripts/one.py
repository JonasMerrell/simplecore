# build one part's document script + verification
import json, sys
sys.path.insert(0, sys.argv[1])
from emit import emit_part3 as emit_part2
an = json.load(open(sys.argv[2])); out = sys.argv[3]; ref = sys.argv[4]
e = emit_part2(an, "f")
L = ['fn add_all(sk, items) { for it in items { sk.add(it); } }', 'let doc = new_document();'] + e.lines
L += ['doc.export_file("%s.step");' % out, 'doc.save("%s.json");' % out,
      'let a = import_step("%s").solids()[0];' % ref, 'let b = import_step("%s.step").solids();' % out,
      'let bb = b[0]; let x = 0.0; let m = 0.0;',
      'try { x = bb.cut([a], 0.0001).volume(); } catch (e) { x = -1.0; }',
      'try { m = a.cut([bb], 0.0001).volume(); } catch (e) { m = -1.0; }',
      'print("RESULT bodies " + b.len() + " orig " + a.volume() + " rebuilt " + bb.volume() + " extra " + x + " missing " + m);']
open(out + ".rhai", "w").write("\n".join(L) + "\n")
