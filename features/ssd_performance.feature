@all @perf
Feature: SSD Performance Validation
Validate SSD performance under various workload conditions.

@qd
Scenario Outline: <REQ_SSD_13> <REQ_SSD_14> Queue depth scaling validation
Given a VM is launched with NVMe SSD
When I run FIO with queue depth <qd>
Then IOPS should scale linearly with queue depth up to hardware limit
And latency should remain within hardware spec

Examples:
  | qd  |
  | 1   |
  | 16  |
  | 32  |
  | 64  |
  | 128 |

@rw
Scenario Outline: <REQ_SSD_05> Read/write workload mixes
Given a VM is launched with a dedicated NVMe SSD
When I run a <read_pct>/<write_pct> read/write workload for <duration> minutes
Then SSD throughput should remain stable
And latency should remain below <latency> ms

Examples:
  | read_pct | write_pct | duration | latency |
  | 50       | 50        | 30       | 2       |
  | 70       | 30        | 60       | 3       |
  | 90       | 10        | 120      | 5       |

@stress
Scenario Outline: <REQ_SSD_10> <REQ_SSD_11> Sustained high-write endurance
Given a VM is launched with a dedicated NVMe SSD
When I run a sustained <percent>% write FIO workload for <hours> hour
Then the SSD write throughput should remain within 90% of baseline
And no critical errors should occur

Examples:
  | percent | hours |
  | 90      | 1     |
  | 95      | 4     |
  | 100     | 8     |

@latency
Scenario Outline: <REQ_SSD_12> <REQ_SSD_05> Latency validation under VM scaling
Given <vm_count> VMs are launched sharing the same NVMe SSD
When each VM runs random <read_pct>/<write_pct> read/write workloads
Then latency for all VMs should remain below <latency_ms>ms average
And no VM should starve IO

Examples:
  | vm_count | read_pct | write_pct | latency_ms |
  | 3        | 50       | 50        | 2          |
  | 5        | 70       | 30        | 3          |
  | 10       | 90       | 10        | 5          |
