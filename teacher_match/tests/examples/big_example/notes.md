This expected_output.json is a 'snapshot',
made by running the implementation that passes the other tests on input.json (formerly sample_data.json).
Basically this is a characterization test. To regenerate the expected file:

```python
with open('resources/big_example/sample_expected_output.json', 'w') as f:
    json.dump(process_file('resources/big_example/input.json'), f, indent=4)
```