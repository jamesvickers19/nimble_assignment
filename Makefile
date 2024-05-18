
.PHONY: test

# usage: make run file=example.json
# for example: make run file=teacher_match/tests/examples/big_example/input.json output_file=output.json
run:
	python -m main $(file) $(output_file)

test:
	python -m unittest discover teacher_match -v
