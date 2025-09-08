@all @inject
Feature: SSD Fault Injection and Recovery Validation
In order to validate SSD resiliency
As a system tester
I want to inject various fault conditions and ensure the SSD recovers without data corruption or performance degradation

@power_loss
Scenario: <REQ_SSD_25> Random power loss should not cause corruption
Given a VM is launched with a dedicated NVMe SSD
When a random power loss event occurs
Then no data corruption should be detected
And all data blocks should be reported correctly

@hot_unplug
Scenario Outline: <REQ_SSD_06> <REQ_SSD_26> Hot unplug should recover without errors
Given a VM is launched with NVMe SSD
When a hot unplug event occurs
Then no data corruption should be detected
And all data blocks should be reported correctly
And devices should recover and IO metrics should remain acceptable

Examples:
  | vm_setup          |
  | single VM         |
  | multi-VM (2 VMs)  |

@controller_reset
Scenario: <REQ_SSD_26> Controller reset should recover without data corruption
Given a VM is launched with a dedicated NVMe SSD
When a controller reset event occurs
Then no data corruption should be detected
And all data blocks should be reported correctly

@firmware_update
Scenario Outline: <REQ_SSD_17> <REQ_SSD_18> SSD firmware update under load should succeed
Given a mounted SSD volume
When I trigger a firmware update while SSD is under <load_level> load
Then update should complete successfully
And SSD should remain accessible post-update

Examples:
  | load_level |
  | idle       |
  | light      |
  | heavy      |

@qos
Scenario: <REQ_SSD_19> <REQ_SSD_20> <REQ_SSD_21> Multi-tenant QoS enforcement
Given two VMs are launched sharing a single NVMe SSD
When I throttle one VM to 50% max IOPS
Then the other VM should achieve full IOPS
And throttled VM should not exceed assigned IOPS

@latency_spikes
Scenario Outline: <REQ_SSD_08> Latency spikes should remain within acceptable limits
Given a VM is running steady workload
When I inject <spike_count> random latency spikes between 50-200ms
Then SSD latency spikes should not exceed <latency_ms>ms above baseline

Examples:
  | spike_count | latency_ms |
  | 5           | 20         |
  | 10          | 30         |

@endurance
Scenario Outline: <REQ_SSD_23> <REQ_SSD_24> Sustained endurance test should remain stable
Given a mounted SSD volume
When I perform a <runtime> hour sustained sequential write of <size_gb> GB with a block size of <bs_kb> KB
Then the average write throughput should be at least "0.90" GB/s
And the average write latency should be less than "100" microseconds

Examples:
  | runtime | size_gb | bs_kb |
  | 1       | 500     | 128   |
  | 2       | 1000    | 256   |
  | 4       | 2000    | 512   |

@smart_monitoring
Scenario Outline: <REQ_SSD_15> <REQ_SSD_16> SMART monitoring should remain within safe thresholds
Given a VM is launched with NVMe attached
When I poll SMART attributes every <interval> minutes under a <workload> workload
Then temperature should remain below 70C
And reallocated sector count should remain zero

Examples:
  | interval | workload   |
  | 5        | mixed      |
  | 10       | sequential |
