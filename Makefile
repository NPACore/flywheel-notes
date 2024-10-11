.venv: bids-client/ curate-bids/
	python -m virtualenv .venv
	source .venv/bin/activate && pip install -e curate-bids && pip install -e bids-client

bids-client/:
	git clone https://gitlab.com/flywheel-io/public/bids-client/
curate-bids/:
	git clone https://gitlab.com/flywheel-io/scientific-solutions/gears/curate-bids/

