modules:
	go mod tidy
	go mod vendor

build:
	go build -o bin/botkawalpemilu -v .

run:
	./bin/botkawalpemilu
