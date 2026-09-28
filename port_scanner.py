#!/usr/bin/env python3

import socket
import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
    )


def scan_port(host, port, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        result = sock.connect_ex((host, port))

        if result == 0:
            return port, "OPEN"

        return port, None

    except socket.timeout:
        return port, None

    except ConnectionRefusedError:
        return port, None

    except OSError:
        return port, None

    finally:
        sock.close()


def resolve_host(host):
    try:
        return socket.gethostbyname(host)

    except socket.gaierror:
        print(f"[ERROR] Cannot resolve hostname: {host}")
        logging.error(f"Cannot resolve hostname: {host}")
        return None


def main():

    parser = argparse.ArgumentParser(
        description="Simple multithreaded TCP port scanner"
    )

    parser.add_argument(
        "host",
        help="Target hostname or IP address"
    )

    parser.add_argument(
        "-p",
        "--ports",
        default="1-1024",
        help="Port or port range, e.g. 80 or 1-1024"
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=1.0,
        help="Connection timeout in seconds (default: 1)"
    )

    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=50,
        help="Number of scanning threads (default: 50)"
    )

    parser.add_argument(
        "-l",
        "--log",
        default="port_scan.log",
        help="Log file (default: port_scan.log)"
    )

    args = parser.parse_args()

    setup_logging(args.log)

    if args.timeout <= 0:
        print("[ERROR] Timeout must be greater than 0.")
        sys.exit(1)

    if args.workers <= 0:
        print("[ERROR] Number of workers must be greater than 0.")
        sys.exit(1)

    target_ip = resolve_host(args.host)

    if target_ip is None:
        sys.exit(1)

    # Parse port argument
    try:

        if "-" in args.ports:
            start_port, end_port = args.ports.split("-", 1)

            start_port = int(start_port)
            end_port = int(end_port)

        else:
            start_port = int(args.ports)
            end_port = start_port

        if start_port < 1 or end_port > 65535:
            raise ValueError

        if start_port > end_port:
            raise ValueError

    except ValueError:
        print("[ERROR] Invalid port range.")
        print("Examples:")
        print("  -p 80")
        print("  -p 1-1024")
        sys.exit(1)

    ports = range(start_port, end_port + 1)

    print("=" * 60)
    print("TCP PORT SCANNER")
    print("=" * 60)
    print(f"Target : {args.host}")
    print(f"IP     : {target_ip}")
    print(f"Ports  : {start_port}-{end_port}")
    print(f"Threads: {args.workers}")
    print(f"Timeout: {args.timeout}s")
    print(f"Started: {datetime.now()}")
    print("=" * 60)

    logging.info("=" * 60)
    logging.info("TCP PORT SCAN STARTED")
    logging.info(f"Target: {args.host}")
    logging.info(f"IP: {target_ip}")
    logging.info(f"Ports: {start_port}-{end_port}")

    start_time = datetime.now()

    try:

        with ThreadPoolExecutor(
            max_workers=args.workers
        ) as executor:

            futures = {
                executor.submit(
                    scan_port,
                    target_ip,
                    port,
                    args.timeout
                ): port

                for port in ports
            }

            for future in as_completed(futures):

                port = futures[future]

                try:
                    scanned_port, status = future.result()

                    # Print ONLY open ports
                    if status == "OPEN":
                        print(
                            f"[OPEN] Port {scanned_port}"
                        )

                        logging.info(
                            f"OPEN PORT: {scanned_port}"
                        )

                except Exception:
                    # Ignore individual port errors
                    continue

    except KeyboardInterrupt:

        print("\n[!] Scan interrupted by user.")
        logging.warning("Scan interrupted by user.")
        sys.exit(1)

    except Exception as e:

        print(f"\n[ERROR] Scanner failed: {e}")
        logging.error(f"Scanner failed: {e}")
        sys.exit(1)

    end_time = datetime.now()
    duration = end_time - start_time

    print("=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)
    print(f"Finished : {end_time}")
    print(f"Duration : {duration}")
    print(f"Log file : {args.log}")
    print("=" * 60)

    logging.info("SCAN COMPLETE")
    logging.info(f"Duration: {duration}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
