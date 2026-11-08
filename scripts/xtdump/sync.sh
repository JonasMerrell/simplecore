cd $(dirname $0)
sed -n '/^#\[cfg(test)\]/q;p' /home/user/cad-rust-app/src/parasolid.rs > src/parasolid.rs
sed -i 's/Err(_) => self.skipped += 1,/Err(e) => { eprintln!("SKIP {e}"); self.skipped += 1 }/' src/parasolid.rs
cat tail.rs >> src/parasolid.rs
cargo build --release --offline 2>&1 | grep -E "^(error|warning)" -A7
