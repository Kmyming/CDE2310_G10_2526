#!/usr/bin/env python3
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MarkerLogger(Node):
    def __init__(self):
        super().__init__("marker_logger")

        # ---------- CONFIG (edit these) ----------
        self.topic = "/aruco/debug"

        # Rolling buffer rules:
        self.buffer_size = 100     # keep at most 100 in RAM
        self.drop_count = 10       # when overflow happens, drop oldest 10

        # Output paths:
        base_dir = Path("/home/harshiet/Documents/CDE2310")
        self.pretty_log_path = base_dir / "aruco_pretty.log"     # NEW: decoded + formatted
        self.raw_jsonl_path = base_dir / "aruco_debug_raw.jsonl" # optional: keep raw too

        # Enable/disable logs:
        self.write_pretty = True
        self.write_raw_jsonl = False  # set True if you still want raw JSONL backup

        # Terminal printing:
        self.print_preview_chars = 220  # if message isn't valid JSON, show only this many chars
        # ----------------------------------------

        self.buffer = deque()

        # Open files once (append)
        self._fh_pretty = None
        self._fh_raw = None

        base_dir.mkdir(parents=True, exist_ok=True)

        if self.write_pretty:
            self._fh_pretty = self.pretty_log_path.open("a", encoding="utf-8")
            self.get_logger().info(f"Logging PRETTY to: {self.pretty_log_path}")

        if self.write_raw_jsonl:
            self._fh_raw = self.raw_jsonl_path.open("a", encoding="utf-8")
            self.get_logger().info(f"Logging RAW JSONL to: {self.raw_jsonl_path}")

        self.sub = self.create_subscription(String, self.topic, self.cb, 10)
        self.get_logger().info(
            f"Subscribed to {self.topic} | RAM buffer={self.buffer_size} | drop oldest={self.drop_count} on overflow"
        )

    def _trim_if_needed(self):
        if len(self.buffer) > self.buffer_size:
            n_drop = min(self.drop_count, len(self.buffer))
            for _ in range(n_drop):
                self.buffer.popleft()

    @staticmethod
    def _utc_ts() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    @staticmethod
    def _fmt_float(v) -> str:
        return f"{v:.6f}" if isinstance(v, (int, float)) else "None"

    def _write_pretty_line(self, line: str):
        if self._fh_pretty is not None:
            self._fh_pretty.write(line + "\n")
            self._fh_pretty.flush()

    def _write_raw_jsonl(self, raw: str):
        if self._fh_raw is not None:
            record = {
                "ts": self._utc_ts(),
                "topic": self.topic,
                "raw": raw,
                "buf_len": len(self.buffer),
            }
            self._fh_raw.write(json.dumps(record) + "\n")
            self._fh_raw.flush()

    def cb(self, msg: String):
        raw = msg.data

        # Store in RAM
        self.buffer.append(raw)
        self._trim_if_needed()

        # Parse inner JSON (what /aruco/debug publishes)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = None

        # If not JSON, just preview
        if not isinstance(parsed, dict):
            preview = raw[: self.print_preview_chars] + ("..." if len(raw) > self.print_preview_chars else "")
            self.get_logger().info(f"buf={len(self.buffer):3d} | {preview}")
            self._write_raw_jsonl(raw)
            return

        # Heartbeat messages
        if parsed.get("status") == "running":
            node_name = parsed.get("node", "unknown")
            line = f"{self._utc_ts()} | heartbeat: {node_name} | buf={len(self.buffer):3d}"
            self.get_logger().info(line)
            self._write_pretty_line(line)
            self._write_raw_jsonl(raw)
            return

        # Marker detections
        markers = parsed.get("markers", [])
        frame_id = parsed.get("frame_id", "unknown")

        if not isinstance(markers, list) or len(markers) == 0:
            line = f"{self._utc_ts()} | frame={frame_id} | markers=[] | buf={len(self.buffer):3d}"
            self.get_logger().info(line)
            self._write_pretty_line(line)
            self._write_raw_jsonl(raw)
            return

        # Print + log each marker in the message
        for m in markers:
            if not isinstance(m, dict):
                continue

            mid = m.get("id", None)

            t = m.get("tvec_m") or {}
            r = m.get("rvec_rad") or {}

            tx, ty, tz = (t.get("x"), t.get("y"), t.get("z")) if isinstance(t, dict) else (None, None, None)
            rx, ry, rz = (r.get("x"), r.get("y"), r.get("z")) if isinstance(r, dict) else (None, None, None)

            line = (
                f"{self._utc_ts()} | frame={frame_id} | "
                f"ID: {mid}; "
                f"Tvec: x = {self._fmt_float(tx)} , y = {self._fmt_float(ty)} , z = {self._fmt_float(tz)} ; "
                f"rvec: x = {self._fmt_float(rx)} , y = {self._fmt_float(ry)} , z = {self._fmt_float(rz)} "
                f"| buf={len(self.buffer):3d}"
            )

            self.get_logger().info(line)
            self._write_pretty_line(line)

        # Optional raw backup
        self._write_raw_jsonl(raw)

    def destroy_node(self):
        for fh in (self._fh_pretty, self._fh_raw):
            if fh is not None:
                try:
                    fh.close()
                except Exception:
                    pass
        super().destroy_node()


def main():
    rclpy.init()
    node = MarkerLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
