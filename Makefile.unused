
GEMINI_FILES := \
	$(wildcard public_gemini/*.gemini) 

HTML_FILES := \
	$(wildcard public_html/*.html) \
	$(wildcard public_html/*.ico)

GEMINI_TAR := \
	warpengineer.space.gmi.tar.gz

HTML_TAR := \
	warpengineer.space.htm.tar.gz

.PHONY: clean deploy

release: ${GEMINI_TAR} ${HTML_TAR}

${GEMINI_TAR}: ${GEMINI_FILES}
	tar --exclude=*.swp --exclude-backups --exclude-vcs -czf ${GEMINI_TAR} public_gemini

${HTML_TAR}: ${HTML_FILES}
	tar --exclude=*.swp --exclude-backups --exclude-vcs -czf ${HTML_TAR} public_html

clean:
	rm -f ${GEMINI_TAR}
	rm -f ${HTML_TAR}

html:
	# using https://github.com/huntingb/gemtext-html-converter
	mkdir -p converted; \
	rm -f converted/*.html; \
	for f in public_gemini/entries/*.gemini; \
	do \
		File=$$(basename $$f); \
		File2=converted/$${File%%gemini}html; \
		python3 convert_gemtext_file.py $$f $$File2; \
	done

deploy:
	./deploy

