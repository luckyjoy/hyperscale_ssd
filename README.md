# 🚀 SSD Hyperscale Simulation Test Framework

**A Universal Chaos & Performance Framework for NVMe SSDs.**

Simulate hyperscale SSD workloads and fault conditions to validate endurance, performance consistency, and data integrity under stress. This robust framework uses **Python**, **Behave (BDD)**, **SPDK fio**, and **QEMU/QMP** for realistic NVMe device emulation and fault injection. It is designed for seamless integration into **Jenkins CI/CD** pipelines for repeatable chaos and regression testing.

---

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python3)
![Behave](https://img.shields.io/badge/BDD-Behave-green.svg?style=for-the-badge&logo=BDD)
![QEMU](https://img.shields.io/badge/Emulation-QEMU/QMP-red.svg?style=for-the-badge&logo=qemu)
![fio](https://img.shields.io/badge/Workload-SPDK%20fio-yellow.svg?style=for-the-badge&logo=fio)
![Kubernetes](https://img.shields.io/badge/kubernetes-ready-yellow?style=for-the-badge&logo=kubernetes)
![Docker](https://img.shields.io/badge/docker-ready-blue?style=for-the-badge&logo=docker)
![CI/CD](https://img.shields.io/badge/CI/CD-ready-green?style=for-the-badge&logo=cicd)
![Allure Report](https://img.shields.io/badge/report-Allure-orange?style=for-the-badge&logo=allure)

---

## 💡 Project Overview 
This framework is critical for testing the resilience and performance consistency of **hyperscale NVMe SSDs**. It automates the process of workload application, fault injection, and metric verification.

| **Component** | **Technology** | **Role** |
|---------------|----------------|----------|
| Test Runner | **Behave (BDD)** | Executes scenario-driven tests and verifies pass/fail criteria. |
| Workload Generator | **SPDK fio** | Generates realistic, high-performance NVMe I/O workloads. |
| Fault Injection | **QEMU + QMP** | Emulates NVMe devices and injects faults (hot-unplug/plug) via QMP. |
| Latency Simulation | **nbdkit / Python proxy** | Simulates I/O slowdowns and latency spikes. |

---

## 🛠️ Key Test Purposes & Challenges

### 🧪 Test Purposes
* Validate SSD performance under **SPDK fio workloads**.
* Simulate **power-loss (hot-unplug)** and device **hot-plug** events.
* Inject **latency spikes / I/O slowdowns**.
* Observe system resilience, recovery, and workload impact.
* Automatically verify latency, IOPS, and throughput against defined thresholds.
* Integrate into **CI/CD** for repeatable chaos and regression testing.

### 📌 Key Challenges with Hyperscale SSDs
* **Endurance and Longevity:** Simulate sustained high-write workloads to ensure throughput and latency remain stable over time. Hyperscale SSDs must endure constant, high-volume write workloads without wearing out.
* **Performance Consistency & Latency Spikes:** Consistent performance is more critical than peak performance. Maintain predictable IOPS and low latency under mixed workloads and shared stress.
* **Reliability and Data Integrity:** Recover from power loss or hot unplug events without data corruption. The goal is to ensure data remains intact and the device can be brought back online reliably.
* **Multi-tenancy & QoS:** A single SSD is often shared by multiple virtual machines. Validate QoS mechanisms to throttle one VM without affecting others.

---

## 🚀 Getting Started

### 🔧 Prerequisites  
- 🐍 **Python 3.10+** (recommended)  
- 💻 **Linux** or **Windows 11** host operating system.
- ⚙️ **QEMU**, **nbdkit** (Linux), **fio**, and **SPDK** installed and built.

### ⚙️ Installation & Setup

1.  **Clone the repository (Example):**
    ```bash
    git clone [https://github.com/luckyjoy/ssd_hyperscale.git](https://github.com/luckyjoy/ssd_hyperscale.git)
    cd ssd_hyperscale
    ```

2.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Host Dependencies (Linux Example):**
    ```bash
    sudo apt-get update
    sudo apt-get install -y qemu-system-x86 nbdkit nbdkit-filter-delay python3 socat fio git
    ```

4.  **SPDK Setup:**
    ```bash
    git clone [https://github.com/spdk/spdk.git](https://github.com/spdk/spdk.git)
    cd spdk
    git submodule update --init
    ./configure --with-fio=/usr/src/fio
    make -j$(nproc)
    ```

5.  **Create VM Image:**
    ```bash
    qemu-img create -f qcow2 vm-disk.qcow2 10G
    ```
    *(Note: VM image must have **FIO installed** and **SSH enabled** for host access on `localhost:2222`)*

---

## 🔬 Running Tests

### 1. Launch VM

* **Linux:** `python3 qemu-faults/qemu_launch_vm.py`
* **Windows:** `python qemu-faults\qemu_launch_vm.py`

### 2. Normal Workload Test (Inside VM)

```bash
fio spdk_fio_mix.job --output-format=json --output=reports/fio_guest.json
````

### 3\. Inject Faults (Chaos Testing)

| **Fault Type** | **Linux Command** | **Windows Command** |
|:---|:---|:---|
| **Hot-Unplug NVMe** | `python3 qemu-faults/qmp_injector.py --socket /tmp/vm-test.qmp --action remove --device-id nvme0` | `python qemu-faults\qmp_injector.py --socket \\.\pipe\vm-test_qmp --action remove --device-id nvme0` |
| **Hot-Plug NVMe** | `python3 qemu-faults/qmp_injector.py --socket /tmp/vm-test.qmp --action add --device-spec '{"driver":"nvme","drive":"drive0","id":"nvme0"}'` | `python qemu-faults\qmp_injector.py --socket \\.\pipe\vm-test_qmp --action add --device-spec '{"driver":"nvme","drive":"drive0","id":"nvme0"}'` |
| **Latency Spike** | `./qemu-faults/nbdkit_delay_server.sh ./vm-disk.qcow2 10810 100 200` | `python qemu-faults\nbd_delay.py 10810 100` |

### 4\. Automatic Metric Verification

The framework verifies metrics against example thresholds:

  * `MAX_LATENCY_MS = 50`
  * `MIN_IOPS = 1000`
  * `MIN_THROUGHPUT_MB = 50`

### 5\. Running Behave Tests

Execute all BDD scenarios, excluding manual tests, and generate an HTML report:

```bash
behave --tags=@all --exclude "features/manual_tests" -f html-pretty -o reports\automation_report.html
```

-----

## ⚙️ CI/CD Integration

The framework is built for automated, cross-platform execution using a **Jenkins Pipeline**.

### 💻 Jenkins CI/CD Workflow

A sample Jenkins Pipeline stage for fault injection tests:

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

## 🌳 Framework Architecture

```
./                           # Root directory
├─ behave.ini                # Behave runner configuration
├─ build.bat                 # Windows build script
├─ environment.py            # Behave environment setup file
├─ Jenkinsfile               # CI/CD pipeline definition
├─ README.html
├─ README.md
├─ requirements.txt          # Python dependencies
├─ run_full_test.ps1         # PowerShell full test runner
├─ run_full_test.sh          # Bash full test runner
├─ test.txt
├─ data/                     # Data generated by fio (e.g., JSON reports)
│  ├─ fio.txt
│  ├─ fio_guest.json
│  └─ mixed_random_output.json
├─ examples/                 # Example fio job files and QEMU setup files
│  ├─ multi_tenant_stress.fio
│  ├─ nvme_queue_depth_saturate.fio
│  ├─ random_multiIO_stress.fio
│  ├─ write_endurance.fio
│  ├─ latency_spike.io
│  ├─ latency_spike_read_lat.json
│  └─ qemu_ubuntu.bat
├─ features/                 # Behave BDD test specifications
│  ├─ advance_hyperscale.feature
│  ├─ ssd_comparision.feature
│  ├─ ssd_fault_injection.feature
│  ├─ ssd_mixed_io.feature
│  ├─ ssd_performance.feature
│  ├─ manual_tests/           # Tests tagged for manual execution
│  │  ├─ manual_endurance.feature
│  │  ├─ manual_power_cycle.feature
│  │  └─ manual_thermal_throttling.feature
│  └─ steps/                  # Python step definitions for Behave
│     ├─ ssd_comparison.py
│     └─ ssd_steps.py
├─ logs/                     # Runtime logs and collected metrics
│  ├─ execution.log
│  ├─ scenario.log
│  └─ *.log                  # Various action and verification logs
├─ qemu-faults/              # QEMU/QMP scripts for VM launch and fault injection
│  ├─ qemu_launch_vm.py
│  ├─ nbdkit_delay_server.sh
│  ├─ nbd_delay.py
│  ├─ qmp_injector.py
│  └─ fault_runner.sh
├─ allure-report/            # Dynamic history report files
├─ allure-results/           # Behave-Allure raw results directory
├─ spdk/                     # SPDK fio jobfiles (legacy/core)
│  ├─ fio_mixed_rw.job
│  ├─ fio_multi_device.job
│  └─ fio_multi_queue.job
├─ .github/                  # GitHub Actions CI/CD workflows
└─ supports/                 # Utility scripts for reporting, telemetry, and CI/CD integration
   ├─ product.json
   ├─ ssd_requirements.csv
   └─ *.json, *.properties # Other Allure Report support files

```

-----

## ⚠️ Limitations & Capabilities

| **Category** | **Details** |
|:---|:---|
| **Capabilities** | Supports **Windows 11** and **Linux** hosts. Handles **Hot-unplug**, **hot-plug**, and **latency spike** injection. Includes **automatic pass/fail** based on SPDK fio metrics. Ready for **Jenkins CI/CD** automation. |
| **Limitations** | QEMU QMP APIs can differ between versions. Hot-removing devices may leave guest filesystem inconsistent (use ephemeral VM snapshots). `nbdkit --filter=delay` required on Linux; Windows uses Python proxy. Thresholds must be adjusted per workload / SSD type. **SPDK fio JSON output** is required for automated verification. |

-----

## 🤝 Contributing Guidelines

1.  Fork the repository
2.  Create a feature branch
3.  Implement new Behave features, SPDK workloads, or fault injection methods.
4.  Run `behave` locally and verify results.
5.  Submit a Pull Request with a clear description.

-----

## 🪪 License

Released under the **MIT License** — free to use, modify, and distribute.

-----

📬 *Contact:* Bang Thien Nguyen [ontario1998@gmail.com](mailto:ontario1998@gmail.com)

-----

> *“Performance is a feature, and reliability is its foundation.”*


