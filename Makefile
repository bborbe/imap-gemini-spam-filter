.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: run
run: spam-filter

.PHONY: spam-filter
spam-filter:
	python spam_filter.py \
		--imap-server="mail.benjamin-borbe.de" \
		--imap-port="993" \
		--imap-username="$$(teamvault-username --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)" \
		--imap-password="$$(teamvault-password --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)" \
		--gemini-api-key="$$(teamvault-password --teamvault-config ~/.teamvault.json --teamvault-key=eL9BXq)"

.PHONY: list-folders
list-folders:
	python list_folders.py \
		--imap-server="mail.benjamin-borbe.de" \
		--imap-port="993" \
		--imap-username="$$(teamvault-username --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)" \
		--imap-password="$$(teamvault-password --teamvault-config ~/.teamvault.json --teamvault-key=xwXyOn)"

.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
