# Benchmarking Taksks

## Latency Test

To visualize results of test x run the following.

```linux
python -m benchmarking.src.tests.latency
```

Before running any tests of your own, ensure devices are in eachother's 
contacts and able to send messages

To generate new results open `latency.py` and set hyperparameters in main 
to desired values and uncomment the call to `wrap_run_test()`
