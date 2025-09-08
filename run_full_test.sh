#!/bin/bash
set -e
echo '[+] Launching VM...'
python3 qemu-faults/qemu_launch_vm.py &
VM_PID=$!
sleep 5
echo '[+] Running Mixed Read/Write workload...'
fio spdk/fio_mixed_rw.job --output-format=json --output=reports/fio_guest.json
echo '[+] Injecting random latency spikes...'
for i in {1..5}; do
    DELAY=$((RANDOM % 151 + 50))
    ./qemu-faults/nbdkit_delay_server.sh ./vm-disk.qcow2 10810 $DELAY
    sleep $((RANDOM % 15 + 5))
done
echo '[+] Injecting power loss and recovery...'
for i in {1..3}; do
    python3 qemu-faults/qmp_injector.py --socket /tmp/vm-test.qmp --action remove --device-id nvme0
    sleep 10
    python3 qemu-faults/qmp_injector.py --socket /tmp/vm-test.qmp --action add --device-spec '{"driver":"nvme","drive":"drive0","id":"nvme0"}'
    sleep 30
done
echo '[+] Running Behave for automated verification...'
behave --tags=@linux features/ssd_fault_injection.feature
echo '[+] Test completed, shutting down VM...'
kill $VM_PID