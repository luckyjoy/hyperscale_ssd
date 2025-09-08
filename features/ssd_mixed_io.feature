@all @mixed
Feature: SSD Hyperscale Reliability and Longevity
Simulate long-running, mixed I/O workloads to test an SSD's
endurance and performance stability over time.

@stress
Scenario Outline: <REQ_SSD_22> Mixed Random Read/Write Workload
Given a mounted SSD volume
And the volume is pre-filled with data
When I perform a sustained mixed random workload with a read/write mix of "<rwmix>"
Then the average read IOPS should be at least "<read_iops>"
And the average write IOPS should be at least "<write_iops>"

Examples:
  | rwmix | read_iops | write_iops |
  | 70/30 | 150000    | 50000      |
  | 50/50 | 120000    | 120000     |
  | 30/70 | 50000     | 150000     |

@endurance @longevity
Scenario Outline: <REQ_SSD_23> <REQ_SSD_24> Prolonged Endurance Test
Given a mounted SSD volume
And the volume is pre-filled with data
When I perform a "<runtime>" hour sustained sequential write of "<size_gb>" GB with a block size of "<bs_kb>" KB
Then the average write throughput should be at least "<throughput>" GB/s
And the average write latency should be less than "<latency>" microseconds

Examples:
  | runtime | size_gb | bs_kb | throughput | latency |
  | 1       | 500     | 128   | 0.90       | 100     |
  | 2       | 1000    | 256   | 0.90       | 100     |
  | 4       | 2000    | 512   | 0.90       | 100     |
