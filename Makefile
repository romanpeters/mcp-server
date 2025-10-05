install:
	uv pip install -r requirements.txt

serve:
	.venv/bin/python server.py

test:
	uv pip install -r requirements-dev.txt
	.venv/bin/pytest