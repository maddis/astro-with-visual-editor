# Initialize
# Check if virtual environment exists, if not create it
init:
	echo "\tChecking for virtual environment..."
	if [ ! -d ".venv" ]; then \
		echo "\tCreating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	echo "\tActivating virtual environment..."
	source .venv/bin/activate
	echo "\tInstalling dependencies..."
	npm install
	pip install -r requirements.txt

activate:
	echo "\tActivating virtual environment..."
	source .venv/bin/activate

fetch:
	echo "\tFetching branches..."
	python3 scripts/fetch_branches.py 20
	

