fmt:
	cd program && cargo fmt
	cd server && cargo fmt
	cd solve && cargo fmt

generate-distfiles:
	rm -rf distfiles
	mkdir distfiles
	cp -r challenge program server compose.yaml compose.develop.yaml distfiles/
	cp README.dist.md distfiles/README.md
	find distfiles -name "target" -type d -exec rm -rf {} + 2>/dev/null || true
	find distfiles -name "Cargo.lock" -type f -delete 2>/dev/null || true
	find distfiles -name ".DS_Store" -type f -delete 2>/dev/null || true
	rm distfiles/challenge/flag.txt
	echo "07CTF{*** REDACTED ***}" > distfiles/challenge/flag.txt
	gtar -czf distfiles.tar.gz distfiles/
