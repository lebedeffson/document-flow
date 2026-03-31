#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys


SERVICES = {
    "workspace": {
        "label": "ONLYOFFICE Workspace",
        "requirements": {
            "cpu_cores": 4,
            "ram_gib": 8,
            "swap_gib": 6,
            "disk_gib": 40,
        },
        "source": "official deployment minimum",
    },
    "docspace": {
        "label": "ONLYOFFICE DocSpace",
        "requirements": {
            "cpu_cores": 6,
            "ram_gib": 12,
            "swap_gib": 6,
            "disk_gib": 40,
        },
        "source": "official deployment minimum",
    },
}

LOW_MEMORY_PROFILE = {
    "label": "Same-host low-memory profile",
    "requirements": {
        "cpu_cores": 6,
        "ram_gib": 14,
        "swap_gib": 6,
        "disk_gib": 80,
    },
    "notes": [
        "Allowed only for low-load first deployment / pilot operation",
        "Workspace full-text search should be disabled after initial bootstrap",
        "Calendar/basic portal remain available; this is not a full-capacity office host",
    ],
}


def bytes_to_gib(value: int) -> float:
    return round(value / (1024 ** 3), 2)


def read_free_bytes():
    result = subprocess.run(["free", "-b"], text=True, capture_output=True, check=True)
    ram_total = 0
    swap_total = 0
    for line in result.stdout.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "Mem:":
            ram_total = int(parts[1])
        elif parts[0] == "Swap:":
            swap_total = int(parts[1])
    return ram_total, swap_total


def read_disk_bytes(path: str = "/"):
    usage = shutil.disk_usage(path)
    return usage.total, usage.free


def evaluate(requirements, host):
    failures = []
    if host["cpu_cores"] < requirements["cpu_cores"]:
        failures.append(f"cpu cores {host['cpu_cores']} < {requirements['cpu_cores']}")
    if host["ram_gib"] < requirements["ram_gib"]:
        failures.append(f"ram {host['ram_gib']} GiB < {requirements['ram_gib']} GiB")
    if host["swap_gib"] < requirements["swap_gib"]:
        failures.append(f"swap {host['swap_gib']} GiB < {requirements['swap_gib']} GiB")
    if host["disk_free_gib"] < requirements["disk_gib"]:
        failures.append(f"disk_free {host['disk_free_gib']} GiB < {requirements['disk_gib']} GiB")
    return failures


def main():
    ram_total_b, swap_total_b = read_free_bytes()
    disk_total_b, disk_free_b = read_disk_bytes("/")

    host = {
        "cpu_cores": int(subprocess.run(["nproc"], text=True, capture_output=True, check=True).stdout.strip()),
        "ram_gib": bytes_to_gib(ram_total_b),
        "swap_gib": bytes_to_gib(swap_total_b),
        "disk_total_gib": bytes_to_gib(disk_total_b),
        "disk_free_gib": bytes_to_gib(disk_free_b),
    }

    results = {}
    for key, meta in SERVICES.items():
        failures = evaluate(meta["requirements"], host)
        results[key] = {
            "label": meta["label"],
            "source": meta["source"],
            "requirements": meta["requirements"],
            "status": "ready" if not failures else "not_ready",
            "failures": failures,
        }

    combined_requirements = {
        "cpu_cores": max(SERVICES["workspace"]["requirements"]["cpu_cores"], SERVICES["docspace"]["requirements"]["cpu_cores"]),
        "ram_gib": SERVICES["workspace"]["requirements"]["ram_gib"] + SERVICES["docspace"]["requirements"]["ram_gib"],
        "swap_gib": SERVICES["workspace"]["requirements"]["swap_gib"] + SERVICES["docspace"]["requirements"]["swap_gib"],
        "disk_gib": SERVICES["workspace"]["requirements"]["disk_gib"] + SERVICES["docspace"]["requirements"]["disk_gib"],
    }
    combined_failures = evaluate(combined_requirements, host)
    low_memory_failures = evaluate(LOW_MEMORY_PROFILE["requirements"], host)

    payload = {
        "host": host,
        "services": results,
        "combined_same_host": {
            "status": "ready" if not combined_failures else "not_ready",
            "requirements": combined_requirements,
            "failures": combined_failures,
        },
        "low_memory_same_host_pilot": {
            "status": "ready" if not low_memory_failures else "not_ready",
            "requirements": LOW_MEMORY_PROFILE["requirements"],
            "failures": low_memory_failures,
            "notes": LOW_MEMORY_PROFILE["notes"],
        },
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not combined_failures else 1


if __name__ == "__main__":
    sys.exit(main())
