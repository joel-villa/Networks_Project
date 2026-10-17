# Benchmarking Taksks

## Latency Test

To visualize results of test 1 run the following from root.

```linux
python -m benchmarking.src.tests.latency
```

Before running any tests of your own, ensure devices are in eachother's 
contacts and able to send messages. Then...

To generate new results open `latency.py` and set hyperparameters in main 
to desired values and uncomment the call to `wrap_run_test()`

## TODOs

### Implementation

- [ ] Expose Timeout Time as Hyper param of latency tests
- [ ] Frame Loss Rate Test
- [ ] Code distance between node checking (using GPS presumably)
- [ ] Code Sender
- [ ] Code Reciever
- [ ] Code SendRecv
- [ ] Code TimeKeeper
- [ ] Code DUT 
- [ ] Code Tested -- Is this one still necessary?

### Testing 

- [ ] Distance Test
- [ ] Multihopping Test
- [ ] Elevation Test
