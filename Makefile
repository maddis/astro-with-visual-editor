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
	pip install -r scripts/requirements-dev.txt

activate:
	echo "\tActivating virtual environment..."
	source .venv/bin/activate

fetch:
	echo "\tFetching branches..."
	python3 scripts/fetch_branches.py 5
	echo "\tFetching blogs..."
	python3 scripts/fetch_blogs.py 5

# Check for uncommitted changes, build, and push to git
push:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: You have uncommitted changes. Please commit or stash them first."; \
		exit 1; \
	fi
	@echo "\tRunning build..."
	@if ! npm run build; then \
		echo "Build failed. Fix the issues and try again."; \
		exit 1; \
	fi
	@echo "\tPushing to git repository..."
	@git push


