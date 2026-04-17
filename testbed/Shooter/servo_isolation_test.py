#!/usr/bin/env python3

"""Standalone SG90/MG90 isolation tester.

Purpose:
- Drive only one servo at a time (no threading, no ROS).
- Help verify whether repeated/extra movement is electrical or software-trigger related.

Usage examples:
  python3 servo_isolation_test.py --interactive
  python3 servo_isolation_test.py --mode sg90 --cycles 5
  python3 servo_isolation_test.py --mode mg90 --cycles 5
  python3 servo_isolation_test.py --mode both --cycles 3
"""

from __future__ import annotations

import argparse
import sys
import time

import pigpio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SG90/MG90 one-at-a-time isolation tester")

    parser.add_argument("--host", default="localhost", help="pigpiod host")
    parser.add_argument("--port", type=int, default=8888, help="pigpiod port")

    parser.add_argument("--gate-pin", type=int, default=12, help="SG90 gate pin")
    parser.add_argument("--rack-pin", type=int, default=13, help="MG90 rack pin")

    parser.add_argument(
        "--mode",
        choices=["sg90", "mg90", "both"],
        default="both",
        help="Non-interactive test mode",
    )
    parser.add_argument("--cycles", type=int, default=3, help="Cycles for non-interactive mode")
    parser.add_argument("--interactive", action="store_true", help="Run interactive menu mode")

    # SG90 params
    parser.add_argument("--gate-open-us", type=int, default=500, help="SG90 open pulsewidth")
    parser.add_argument("--gate-close-us", type=int, default=1500, help="SG90 close pulsewidth")
    parser.add_argument("--gate-settle-s", type=float, default=0.25, help="SG90 settle delay")

    # MG90 params (continuous)
    parser.add_argument("--rack-neutral-us", type=int, default=1500, help="MG90 neutral pulsewidth")
    parser.add_argument("--rack-engage-us", type=int, default=1200, help="MG90 engage pulsewidth")
    parser.add_argument("--rack-engage-s", type=float, default=0.68, help="MG90 engage duration")
    parser.add_argument("--rack-disengage-us", type=int, default=1000, help="MG90 disengage pulsewidth")
    parser.add_argument("--rack-disengage-s", type=float, default=0.24, help="MG90 disengage duration")
    parser.add_argument("--rack-hold-s", type=float, default=0.20, help="Hold at neutral between phases")

    parser.add_argument("--between-cycles-s", type=float, default=0.50, help="Pause between cycles")
    return parser


class ServoIsolationTester:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.command_counter = 0
        self.pi = pigpio.pi(args.host, args.port)
        if not self.pi.connected:
            raise RuntimeError(f"Could not connect to pigpiod at {args.host}:{args.port}")

        self._set_pw(args.gate_pin, args.gate_close_us, "INIT SG90 close")
        self._set_pw(args.rack_pin, args.rack_neutral_us, "INIT MG90 neutral")

    def _set_pw(self, pin: int, pulsewidth_us: int, note: str) -> None:
        self.command_counter += 1
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] CMD#{self.command_counter:03d} pin={pin} pw={pulsewidth_us}us :: {note}")
        self.pi.set_servo_pulsewidth(pin, pulsewidth_us)

    def sg90_cycle(self, idx: int) -> None:
        print(f"\n[SG90] Cycle {idx}")
        # Keep MG90 stable while SG90 is tested.
        self._set_pw(self.args.rack_pin, self.args.rack_neutral_us, "Hold MG90 neutral")

        self._set_pw(self.args.gate_pin, self.args.gate_open_us, "SG90 open gate")
        time.sleep(self.args.gate_settle_s)
        self._set_pw(self.args.gate_pin, self.args.gate_close_us, "SG90 close gate")
        time.sleep(self.args.gate_settle_s)

    def mg90_cycle(self, idx: int) -> None:
        print(f"\n[MG90] Cycle {idx}")
        # Keep SG90 stable while MG90 is tested.
        self._set_pw(self.args.gate_pin, self.args.gate_close_us, "Hold SG90 closed")

        self._set_pw(self.args.rack_pin, self.args.rack_engage_us, "MG90 engage")
        time.sleep(self.args.rack_engage_s)
        self._set_pw(self.args.rack_pin, self.args.rack_neutral_us, "MG90 neutral after engage")
        time.sleep(self.args.rack_hold_s)

        self._set_pw(self.args.rack_pin, self.args.rack_disengage_us, "MG90 disengage")
        time.sleep(self.args.rack_disengage_s)
        self._set_pw(self.args.rack_pin, self.args.rack_neutral_us, "MG90 neutral after disengage")
        time.sleep(self.args.rack_hold_s)

    def run_non_interactive(self) -> None:
        for i in range(1, self.args.cycles + 1):
            if self.args.mode in ("sg90", "both"):
                self.sg90_cycle(i)
                time.sleep(self.args.between_cycles_s)

            if self.args.mode in ("mg90", "both"):
                self.mg90_cycle(i)
                time.sleep(self.args.between_cycles_s)

    def run_interactive(self) -> None:
        print("\nInteractive commands:")
        print("  g = one SG90 cycle")
        print("  r = one MG90 cycle")
        print("  b = SG90 then MG90")
        print("  q = quit")

        i = 1
        while True:
            cmd = input("\nCommand [g/r/b/q]: ").strip().lower()
            if cmd == "q":
                break
            if cmd == "g":
                self.sg90_cycle(i)
            elif cmd == "r":
                self.mg90_cycle(i)
            elif cmd == "b":
                self.sg90_cycle(i)
                time.sleep(self.args.between_cycles_s)
                self.mg90_cycle(i)
            else:
                print("Unknown command")
                continue
            i += 1

    def shutdown(self) -> None:
        try:
            self._set_pw(self.args.gate_pin, 0, "Disable SG90 pulses")
            self._set_pw(self.args.rack_pin, 0, "Disable MG90 pulses")
        finally:
            self.pi.stop()
            print("pigpio connection closed")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    tester = None
    try:
        tester = ServoIsolationTester(args)
        if args.interactive:
            tester.run_interactive()
        else:
            tester.run_non_interactive()
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if tester is not None:
            tester.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
