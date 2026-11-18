#!/usr/bin/env python3
"""
meshcore_fuzz.py - packet fuzzer for MeshCore nodes YOU OWN.

Use only on your own devices, on a private frequency / attenuated or shielded
setup, so nothing reaches anyone else's network.

Architecture:
  [this script] --serial--> [attacker LoRa board] ~~radio~~> [target node]
                                                                  |
  [this script] <--serial (log output)---------------------------+

The attacker board runs a tiny sketch that reads one hex-encoded packet per
line from serial and transmits it raw (see TRANSPORT PROTOCOL below).
The target's USB serial log is watched for crashes / reboots.

Packet layout assumed (verify against src/Packet.h in your firmware version):
  [header:1] [transport_codes:4 if route type is 0 or 3] [path_len:1]
  [path:path_len] [payload:...]
  header bits: 0-1 route type, 2-5 payload type, 6-7 payload version

TRANSPORT PROTOCOL (serial to attacker board):
  host -> board:  "<hex>\n"   board transmits those bytes as one LoRa frame

Examples:
  python3 meshcore_fuzz.py --transport dryrun --iterations 50
  python3 meshcore_fuzz.py --transport serial --tx-port /dev/ttyUSB0 \
      --monitor-port /dev/ttyUSB1 --delay 2.0 --iterations 5000 --seed 1234
  python3 meshcore_fuzz.py --seed-file captured.txt --mode mutate
"""
import argparse
import collections
import json
import os
import random
import re
import sys
import threading
import time


ROUTE_TRANSPORT_FLOOD = 0
ROUTE_FLOOD = 1
ROUTE_DIRECT = 2
ROUTE_TRANSPORT_DIRECT = 3
TRANSPORT_ROUTES = (ROUTE_TRANSPORT_FLOOD, ROUTE_TRANSPORT_DIRECT)

MAX_PATH = 64        
MAX_PAYLOAD = 150   
MAX_FRAME = 255     

INTERESTING_BYTES = [0x00, 0x01, 0x02, 0x7F, 0x80, 0xFE, 0xFF]


CRASH_PATTERN = re.compile(
    r"Guru Meditation|Backtrace|panic|abort\(\)|assert failed|rst:0x|"
    r"Stack smashing|stack overflow|HardFault|MemManage|BusFault|"
    r"watchdog|WDT|brownout|ets [A-Z][a-z]{2} \d+ 20\d\d",
    re.IGNORECASE,
)



def make_header(route, ptype, version=0):
    return (route & 0x3) | ((ptype & 0xF) << 2) | ((version & 0x3) << 6)


def build_packet(route, ptype, path, payload, version=0,
                 transport_codes=None, path_len_override=None):
    out = bytearray([make_header(route, ptype, version)])
    if route in TRANSPORT_ROUTES:
        out += transport_codes if transport_codes is not None else os.urandom(4)
    plen = len(path) if path_len_override is None else path_len_override
    out.append(plen & 0xFF)
    out += path
    out += payload
    return bytes(out[:MAX_FRAME])



def weighted_length(rng, limit):
    """Bias toward boundary values, where parsers tend to break."""
    boundaries = [0, 1, 2, 3, 4, 5, 6, 7, 15, 16, 17, 31, 32, 33,
                  limit - 1, limit, limit + 1]
    if rng.random() < 0.5:
        return max(0, rng.choice(boundaries))
    return rng.randint(0, limit)


def random_bytes(rng, n):
    mode = rng.random()
    if mode < 0.6:
        return bytes(rng.getrandbits(8) for _ in range(n))
    if mode < 0.8:
        return bytes([rng.choice(INTERESTING_BYTES)]) * n
    return bytes(rng.choice(INTERESTING_BYTES) for _ in range(n))


def gen_structured(rng):
    """Valid-looking header, random contents."""
    route = rng.randint(0, 3)
    ptype = rng.randint(0, 15)
    version = rng.choice([0, 0, 0, 1, 2, 3])
    path = random_bytes(rng, weighted_length(rng, MAX_PATH))
    payload = random_bytes(rng, weighted_length(rng, MAX_PAYLOAD))
    plo = None
    if rng.random() < 0.2:           # lie about the path length
        plo = rng.choice([0, 1, len(path) + 1, len(path) - 1,
                          MAX_PATH, MAX_PATH + 1, 127, 128, 255])
    return build_packet(route, ptype, path, payload, version,
                        path_len_override=plo)


def gen_peer_like(rng):
    """Shaped like an encrypted peer message: [dest:1][src:1][mac/nonce][ct].
    Exercises decrypt/auth paths: bad tags, short ciphertexts, odd lengths."""
    route = rng.choice([ROUTE_FLOOD, ROUTE_DIRECT])
    ptype = rng.choice([0x00, 0x01, 0x02, 0x08])   # REQ, RESPONSE, TXT, PATH
    path = random_bytes(rng, rng.randint(0, 8))
    body = bytes([rng.getrandbits(8), rng.getrandbits(8)])
    body += random_bytes(rng, weighted_length(rng, 100))
    return build_packet(route, ptype, path, body)


def gen_raw(rng):
    """Completely unstructured bytes."""
    return random_bytes(rng, rng.randint(1, MAX_FRAME))



def mut_bitflip(rng, b):
    if not b:
        return b
    a = bytearray(b)
    for _ in range(rng.choice([1, 1, 2, 4])):
        i = rng.randrange(len(a))
        a[i] ^= 1 << rng.randrange(8)
    return bytes(a)


def mut_byteset(rng, b):
    if not b:
        return b
    a = bytearray(b)
    a[rng.randrange(len(a))] = rng.choice(INTERESTING_BYTES)
    return bytes(a)


def mut_truncate(rng, b):
    return b[:rng.randint(0, len(b))] if b else b


def mut_extend(rng, b):
    return (b + random_bytes(rng, rng.randint(1, 64)))[:MAX_FRAME]


def mut_dupchunk(rng, b):
    if len(b) < 2:
        return b
    i = rng.randrange(len(b))
    j = rng.randint(i + 1, len(b))
    return (b[:j] + b[i:j] + b[j:])[:MAX_FRAME]


def mut_header(rng, b):
    if not b:
        return b
    return bytes([rng.getrandbits(8)]) + b[1:]


def mut_pathlen(rng, b):
    """Corrupt the path_len byte (position depends on route type)."""
    if len(b) < 2:
        return b
    idx = 5 if (b[0] & 3) in TRANSPORT_ROUTES else 1
    if idx >= len(b):
        return b
    a = bytearray(b)
    a[idx] = rng.choice([0, 1, MAX_PATH - 1, MAX_PATH, MAX_PATH + 1,
                         127, 128, 255])
    return bytes(a)


MUTATORS = [mut_bitflip, mut_byteset, mut_truncate, mut_extend,
            mut_dupchunk, mut_header, mut_pathlen]


def mutate(rng, seed_pkt):
    out = seed_pkt
    for _ in range(rng.choice([1, 1, 2, 3])):
        out = rng.choice(MUTATORS)(rng, out)
    return out[:MAX_FRAME]


class SerialTransport:
    def __init__(self, port, baud):
        import serial  # pip install pyserial
        self.ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)  # many boards reset when the port opens

    def send(self, pkt):
        self.ser.write(pkt.hex().encode() + b"\n")
        self.ser.flush()

    def close(self):
        self.ser.close()



class CrashMonitor(threading.Thread):
    """Watches the target's serial log and records packets around any crash."""

    def __init__(self, port, baud, history, outdir):
        super().__init__(daemon=True)
        import serial
        self.ser = serial.Serial(port, baud, timeout=1)
        self.history = history
        self.outdir = outdir
        self.crashes = 0
        self.last_crash = threading.Event()
        self.recent_lines = collections.deque(maxlen=40)
        self.running = True

    def run(self):
        while self.running:
            try:
                line = self.ser.readline().decode(errors="replace").rstrip()
            except Exception:
                continue
            if not line:
                continue
            self.recent_lines.append(line)
            if CRASH_PATTERN.search(line):
                self.record(line)

    def record(self, trigger):
        self.crashes += 1
        path = os.path.join(self.outdir, f"crash_{self.crashes:03d}.json")
        with open(path, "w") as f:
            json.dump({
                "trigger_line": trigger,
                "log_tail": list(self.recent_lines),
                # Reset may be delayed, so inspect several recent packets.
                "last_packets": list(self.history),
            }, f, indent=2)
        print(f"\n[!] possible crash #{self.crashes}: {trigger}\n    -> {path}")
        self.last_crash.set()




def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transport", choices=["dryrun", "serial"], default="dryrun")
    ap.add_argument("--tx-port", help="serial port of the attacker LoRa board")
    ap.add_argument("--tx-baud", type=int, default=115200)
    ap.add_argument("--monitor-port", help="serial port of the TARGET node's log")
    ap.add_argument("--monitor-baud", type=int, default=115200)
    ap.add_argument("--iterations", type=int, default=1000)
    ap.add_argument("--delay", type=float, default=2.0,
                    help="seconds between packets (must exceed LoRa airtime)")
    ap.add_argument("--seed", type=int, default=None, help="RNG seed (reproducible)")
    ap.add_argument("--mode", choices=["generate", "mutate", "both"], default="both")
    ap.add_argument("--seed-file", help="file of captured packets, one hex per line")
    ap.add_argument("--outdir", default="fuzz_out")
    ap.add_argument("--pause-on-crash", type=float, default=10.0,
                    help="seconds to wait after a crash for the node to reboot")
    args = ap.parse_args()

    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(2**32)
    rng = random.Random(seed)
    os.makedirs(args.outdir, exist_ok=True)
    print(f"RNG seed: {seed}  (pass --seed {seed} to reproduce)")

    seeds = load_seeds(args.seed_file) if args.seed_file else []
    if args.mode in ("mutate", "both") and not seeds:
        if args.mode == "mutate":
            sys.exit("--mode mutate needs --seed-file with captured packets")
        print("no seed file: mutation disabled, generating only")

    history = collections.deque(maxlen=50)
    if args.transport == "serial":
        if not args.tx_port:
            sys.exit("--tx-port required for serial transport")
        tx = SerialTransport(args.tx_port, args.tx_baud)
    else:
        tx = DryRunTransport()

    monitor = None
    if args.monitor_port:
        monitor = CrashMonitor(args.monitor_port, args.monitor_baud, history, args.outdir)
        monitor.start()

    log = open(os.path.join(args.outdir, "sent.jsonl"), "a")
    generators = [gen_structured, gen_structured, gen_peer_like, gen_raw]

    try:
        for n in range(args.iterations):
            if seeds and args.mode in ("mutate", "both") and (
                    args.mode == "mutate" or rng.random() < 0.5):
                pkt, strategy = mutate(rng, rng.choice(seeds)), "mutate"
            else:
                g = rng.choice(generators)
                pkt, strategy = g(rng), g.__name__

            # Log BEFORE sending so a crash can be tied to its trigger packet.
            rec = {"n": n, "t": time.time(), "strategy": strategy,
                   "len": len(pkt), "hex": pkt.hex()}
            history.append(rec)
            log.write(json.dumps(rec) + "\n")
            log.flush()

            tx.send(pkt)
            print(f"\r[{n + 1}/{args.iterations}] {strategy:<15} {len(pkt):>3}B",
                  end="", flush=True)

            if monitor and monitor.last_crash.is_set():
                monitor.last_crash.clear()
                print(f"\n    pausing {args.pause_on_crash}s for reboot...")
                time.sleep(args.pause_on_crash)
            else:
                time.sleep(args.delay if args.transport == "serial" else 0)
    except KeyboardInterrupt:
        print("\ninterrupted")
    finally:
        tx.close()
        log.close()
        if monitor:
            monitor.running = False
        print(f"\ndone. crashes flagged: {monitor.crashes if monitor else 'n/a (no monitor)'}")
        print(f"packet log: {os.path.join(args.outdir, 'sent.jsonl')}")


if __name__ == "__main__":
    main()