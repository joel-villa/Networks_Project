# Benchmarking Taksks

## Latency Test

To visualize the latency test results:

```linux
cd benchmarking
python -m src.latency.LatencyResults
```

Before running any tests of your own, ensure devices are in eachother's 
contacts and able to send messages. Then...

- Setup .env to have: `MESH_PATH = "<path>/<to>/<USB>/<Serial>/<Device>"`
- Set the `contact_under_test` to the contact name of the device that will be 
 tested
- Set `src_type`, and `dst_type` to appropraite devices
- Set other hyperparameters as desired
- Run `python -m src.latency.main`

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
hyperparameters in main to desired values, and run `python -m src.loss.main`

## TODOs

### Implementation

- [ ] Expose Timeout Time as Hyper param of latency tests
- [ ] Distance tests
- [ ] Box plots on latency tests

### Testing 

- [ ] Distance Test
- [ ] Multihopping Test
- [ ] Elevation Test
