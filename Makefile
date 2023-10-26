.PHONY: clean

clean:
	find . -name '*.pyc' -delete
	find . -name '__pyache__' -type d exec rm -rf {} +