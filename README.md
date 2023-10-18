# neo4j_lightbulb_problem

Hi Neo4j Team,
This is my submission of the Lightbulb Problem task. I have tried to follow the requirements as closely as possible.

---
## Running the tests
Run the tests to ensure that everything is in order by go to the root of the project and run the `run_tests.sh` script

## Running the CLI tool
To run the CLI tool, you simply need to execute the `run.sh` script. The CLI tool will accept input until it sees an `EOF`. You can add energy logs line by line or also copy a number of energy logs (separated by a `\n` character) and enter them altogether.

Examples to try 
```
> 1544206562 TurnOff
> 1544206563 Delta +0.5
> 1544210163 TurnOff
> EOF

# Expected result: Estimated energy used: 2.5 Wh
```

```
> 1544206562 TurnOff
> 1544206563 Delta +0.5
> 1544210163 Delta -0.25
> 1544210163 Delta -0.25
> 1544211963 Delta +0.75
> 1544213763 TurnOff
EOF

# Expected result: Estimated energy used: 5.625 Wh
```

```
> 1544206562 TurnOff
> 1544206563 TurnOff
> 1544210163 Delta +0.5
> EOF

# Expected result: Estimated energy used: 0.0 Wh
```