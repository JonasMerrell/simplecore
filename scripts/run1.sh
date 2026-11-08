#!/bin/bash
# run1.sh <body id> [axis]
S=/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad; b=$1; ax=${2:--1}
cd /home/user/cad-rust-app
(echo "let IN = \"$S/parts/b$b.step\"; let OUT = \"$S/an/b$b.json\"; let AX = $ax;"; cat $S/gen/analyze2.rhai) > $S/an/r$b.rhai
timeout 900 ./target/release/rcad script $S/an/r$b.rhai 2>&1 | tail -3
python3 $S/gen/one.py $S/gen $S/an/b$b.json $S/build/b$b $S/parts/b$b.step && timeout 900 ./target/release/rcad script $S/build/b$b.rhai 2>&1 | tail -3
(echo "let A=\"$S/parts/b$b.step\"; let B=\"$S/build/b$b.step\"; let OUT=\"$S/build/b$b.png\";"; cat $S/gen/cmp.rhai) > $S/c$b.rhai; ./target/release/rcad script $S/c$b.rhai 2>&1 | tail -2
