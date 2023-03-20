VERSION 	= 2.0.0
PREFIX     ?= /usr
CONFDIR    ?= /etc
OUTPATH	    = ./bin
TPMPATH 	= $(DESTDIR)/tmp/KEENTUNE
BINDIR      = $(DESTDIR)$(PREFIX)/bin
LOCALBINDIR = $(DESTDIR)$(PREFIX)/local/bin
SYSCONFDIR  = $(DESTDIR)$(CONFDIR)/keentune/bench
SYSTEMDDIR  = $(DESTDIR)$(PREFIX)/lib/systemd/system

all: target

target:
	pyinstaller --clean --onefile \
		--workpath $(TPMPATH) \
		--distpath $(OUTPATH) \
		--specpath $(TPMPATH) \
		--name keentune-bench \
		bench/bench.py

clean:
	rm -rf $(TPMPATH)
	rm -rf $(OUTPATH)
	rm -rf $(BINDIR)/keentune-bench
	rm -rf $(LOCALBINDIR)/keentune-bench
	rm -rf keentune-bench-$(VERSION).tar.gz

install: 
	@echo "+ Start installing KeenTune-bench"
	mkdir -p $(SYSCONFDIR)
	mkdir -p $(SYSTEMDDIR)
	install -p -D -m 0644 bench/bench.conf $(SYSCONFDIR)
	install -p -D -m 0644 keentune-bench.service $(SYSTEMDDIR)
	mkdir -p $(BINDIR)
	mkdir -p $(LOCALBINDIR)
	cp $(OUTPATH)/* $(BINDIR)
	cp $(OUTPATH)/* $(LOCALBINDIR)
	@echo "+ Make install Done."

startup:
	systemctl daemon-reload
	systemctl restart keentune-bench

tar:
	mkdir -p keentune-bench-$(VERSION)
	cp  --parents $(OUTPATH)/* \
		keentune-bench.service \
		LICENSE \
		Makefile \
		bench/bench.conf \
		keentune-bench-$(VERSION)
	tar -czvf keentune-bench-$(VERSION).tar.gz keentune-bench-$(VERSION)
	rm -rf keentune-bench-$(VERSION)

run: all install startup
rpm: target tar
