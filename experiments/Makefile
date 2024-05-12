PWD = $(shell pwd)

GO = go
OL_DIR = $(abspath ./src)
OL_GO_FILES = $(shell find src/ -name '*.go')
LAMBDA_FILES = $(shell find lambda)

.PHONY: all
.PHONY: install
.PHONY: test-all
.PHONY: clean

all: ol imgs/lambda

imgs/lambda: $(LAMBDA_FILES)
	${MAKE} -C lambda
	docker build -t lambda lambda
	touch imgs/lambda

ol: 
	cd $(OL_DIR) && $(GO) build -o ../ol -mod=vendor

install: ol
	cp ol /usr/local/bin

test-all:
	python3 -u test.py

clean:
	rm -f ol
	rm -f imgs/lambda
	${MAKE} -C lambda clean
	${MAKE} -C sock clean