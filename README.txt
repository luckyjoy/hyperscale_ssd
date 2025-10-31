````markdown
# SSD Hyperscale Simulation Test Framework

**Author:** Bang Thien Nguyen | [ontario1998@gmail.com](mailto:ontario1998@gmail.com)

## Key Challenges with Hyperscale SSDs

* **Endurance and Longevity:** Simulate sustained high-write workloads to ensure throughput and latency remain stable over time. Hyperscale SSDs must endure constant, high-volume write workloads without wearing out.
* **Performance Consistency & Latency Spikes:** Consistent performance is more critical than peak performance. Maintain predictable IOPS and low latency under mixed workloads and shared stress.
* **Reliability and Data Integrity:** Recover from power loss or hot unplug events without data corruption. The goal is to ensure data remains intact and the device can be brought back online reliably.
* **Multi-tenancy & QoS:** A single SSD is often shared by multiple virtual machines. Validate QoS mechanisms to throttle one VM without affecting others.

---

## 📌 Overview

This framework simulates hyperscale SSD workloads and fault conditions using:

* **Python + Behave (BDD)** for scenario-driven testing.
* **SPDK fio jobfiles** for realistic NVMe workloads.
* **QEMU + QMP** for NVMe device emulation and fault injection.
* **nbdkit delay filters (Linux) / Python delay proxy (Windows)** to simulate latency spikes.
* **Jenkins CI/CD pipelines** for automation.

---

## 🧪 Test Purposes

* Validate SSD performance under SPDK fio workloads.
* Simulate power-loss (hot-unplug) and device hot-plug events.
* Inject latency spikes / I/O slowdowns.
* Observe system resilience, recovery, and workload impact.
* Automatically verify latency, IOPS, throughput against thresholds.
* Integrate into CI/CD for repeatable chaos & regression testing.

---

## ⚙️ Setup Instructions

### 1. Host Dependencies

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y qemu-system-x86 nbdkit nbdkit-filter-delay python3 socat fio git
nbdkit --filter=delay file disk.img rdelay=100ms wdelay=100ms
````

**Windows 11:**

  * Install QEMU for Windows ([link](https://qemu.weilnetz.de/))
  * Install Python 3.10+
  * Use Hyper-V (`-accel whpx`) for acceleration

### 2\. Python Dependencies

```bash
pip install -r requirements.txt
```

### 3\. SPDK Setup

```bash
git clone [https://github.com/spdk/spdk.git](https://github.com/spdk/spdk.git)
cd spdk
git submodule update --init
./configure --with-fio=/usr/src/fio
make -j$(nproc)
```

### 4\. VM Image

```bash
qemu-img create -f qcow2 vm-disk.qcow2 10G
```

  * FIO installed in guest
  * SSH enabled for host access (`localhost:2222`)

-----

## 🚀 Running Tests

### 1\. Launch VM

**Linux:**

```bash
python3 qemu-faults/qemu_launch_vm.py
```

**Windows:**

```bash
python qemu-faults\qemu_launch_vm.py
```

### 2\. Normal Workload Test

```bash
fio spdk_fio_mix.job --output-format=json --output=reports/fio_guest.json
```

### 3\. Inject Faults (Chaos Testing)

```bash
# Hot-unplug NVMe
python3 qemu-faults/qmp_injector.py --socket /tmp/vm-test.qmp --action remove --device-id nvme0
python qemu-faults\qmp_injector.py --socket \\.\pipe\vm-test_qmp --action remove --device-id nvme0

# Hot-plug NVme
python3 qemu-faults/qmp_injector.py --socket /tmp/vm-test.qmp --action add --device-spec '{"driver":"nvme","drive":"drive0","id":"nvme0"}'
python qemu-faults\qmp_injector.py --socket \\.\pipe\vm-test_qmp --action add --device-spec '{"driver":"nvme","drive":"drive0","id":"nvme0"}'

# Latency spike
./qemu-faults/nbdkit_delay_server.sh ./vm-disk.qcow2 10810 100 200
python qemu-faults\nbd_delay.py 10810 100
```

### 4\. Automatic Metric Verification

These are example thresholds used by the verification script:

```bash
MAX_LATENCY_MS = 50
MIN_IOPS = 1000
MIN_THROUGHPUT_MB = 50
```

### 5\. Running Tests with Behave

To run all Behave tests (excluding those tagged for manual execution):

```bash
behave --tags=@all --exclude "features/manual_tests" -f html-pretty -o reports\automation_report.html
```

-----

## 💻 Jenkins CI/CD Integration

Example Jenkins Pipeline stage for fault injection tests:

```groovy
stage('Fault Injection Tests') {
  matrix {
    axes { axis { name 'OS'; values 'linux', 'windows' } }
    agent { label "${OS}-agent" }
    stages {
      stage('Run Behave') {
        steps {
          script {
            if ("${OS}" == "windows") {
              bat 'behave --tags=@windows features/ssd_fault_injection.feature'
            } else {
              sh 'behave --tags=@linux features/ssd_fault_injection.feature'
            }
          }
        }
      }
    }
  }
}
```

-----

## 🌳 Repo Structure

```
features/                   # Behave BDD test specs
spdk/                       # SPDK jobfiles
qemu-faults/
  ├── qemu_launch_vm.py       # Launch QEMU VM cross-platform
  ├── nbdkit_delay_server.sh  # Linux latency server
  ├── nbd_delay.py            # Windows latency proxy
  ├── qmp_injector.py         # QMP fault injector
  ├── fault_runner.sh         # Wrapper for chaos faults (Linux)
  └── *.log                   # Logs (runtime)
Jenkinsfile                 # CI/CD pipeline definition
requirements.txt            # Python dependencies
README.html                 # Documentation
```

-----

## ⚠️ Limitations & Capabilities

### Limitations

  * QEMU QMP APIs differ between versions.
  * Hot-removing devices can leave guest filesystem inconsistent; use ephemeral VM snapshots.
  * `nbdkit --filter=delay` required on Linux; Windows uses Python proxy.
  * Thresholds must be adjusted per workload / SSD type.
  * SPDK fio JSON output is required for automated verification.

### Framework Capabilities

  * Supports Windows 11 and Linux hosts.
  * Handles Hot-unplug, hot-plug, and latency spike injection.
  * Includes automatic pass/fail based on SPDK fio metrics.
  * Ready for Jenkins CI/CD automation.

<!-- end list -->

```
```