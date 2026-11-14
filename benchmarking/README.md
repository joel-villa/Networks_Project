# Benchmarking Taksks

## Latency Test

To visualize results of test 2 run the following from root.

```linux
cd benchmarking
python -m src.latency.Latency
```

Before running any tests of your own, ensure devices are in eachother's 
contacts and able to send messages. Then...

To generate new results open `src/latency/Latency.py` and set 
hyperparameters in main to desired values and uncomment the call to 
`wrap_run_test()`

## Loss Test

To visualize
To visualize results of test 5 run the following from root.

```linux
cd benchmarking
python -m src.loss.LossResults
```

Before running any tests of your own, ensure devices are in eachother's 
contacts and able to send messages. Then...

To generate new results open `src/loss/main.py` and set 
hyperparameters in main to desired values

## TODOs

### Implementation

- [ ] Expose Timeout Time as Hyper param of latency tests
- [ ] Distance tests
- [ ] Box plots on latency tests

### Testing 

- [ ] Distance Test
- [ ] Multihopping Test
- [ ] Elevation Test
