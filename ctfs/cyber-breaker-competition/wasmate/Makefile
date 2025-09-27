generate-dist:
	rm -rf dist
	mkdir dist
	DOCKER_DEFAULT_PLATFORM=linux/amd64 docker run --rm -v $(PWD):/src -u $(id -u):$(id -g) emscripten/emsdk emcc src/flag-checker.cpp -o dist/flag-checker.html
	cp src/README.dist.md dist/README.md
