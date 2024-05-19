# Purpose

Matches teachers to principals given data on teachers (credentials, grades, subjects, location)
and principals (location, open roles with subject and grade).

# Using the code

There is a command-line application that takes two arguments:

- input teacher/principal JSON file
- desired output file location

That can be invoked like:

```shell
make run file=teacher_match/tests/examples/big_example/input.json output_file=output.json
```

Or:

```shell
python -m main teacher_match/tests/examples/big_example/input.json output.json
```

Alternatively the implementation (`teacher_match.src.core.match_teachers_to_principals`) can be called directly with a
dictionary which returns a dictionary of results.

Example data inputs can be found in [examples](teacher_match/tests/examples) folder as `input.json` files.

# Testing the code

Run the test suite:

```shell
make test
```

There is one test (`test_process_file_on_examples`) which automatically picks up
example input/output JSON files added to the repo. To add a new example to exercise,
add a folder under [examples](teacher_match/tests/examples) with an input file named `input.json`
and an expected output file named `expected_output.json`. Other files such as a `notes.md` can be added
to that folder for documentation and the test will ignore.

The tests verify returned principal/teacher matches ignoring order (of principals and the teachers they are matched to)
since this is not semantically important, including in tests using `expected_output.json`.

# Matching algorithm

A straightforward implementation of matching teachers to principals would be to
iterate the teachers and for each one, iterate the principals and find matching ones by
location/subject/grade; commit [dfbfcc2f5c713](/../../commit/dfbfcc2f5c713) has this implementation.
This approach is easy to understand and has low memory usage, but the runtime scales
poorly with the number of teachers and principals. On the principals side the main runtime
factor is the total number of open roles among them: this approach has a runtime of `O(T * R)`,
where `T` is the number of teachers and `R` is the number of open roles among all the principals.
This is because this approach is re-searching the open roles again for each teacher.

The current implementation cuts down the runtime to `O(T + R)` at the expense of using `O(R)` space.
It builds a multi-level lookup into principal_id's by the matching attributes (location, grade, subject)
which avoids having to re-search the principals when examining each teacher. This somewhat resembles having indices on a
database table.

The straightforward approach may be preferable if the number of teachers and principals this
algorithm is being used on is below some size, as it may run faster (not building the lookup) and
is easier to understand. The size where the lookup-based algorithm begins to be worth it's complexity could
be determined empirically by benchmarking.

# Improvements

The repository could use some automation on running tests and linting the code.
Github Workflows would be one approach, tried adding one but didn't work out-of-the-box,
needs investigation.
