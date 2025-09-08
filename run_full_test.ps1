Write-Output '[+] Launching VM...'
Start-Process -NoNewWindow -FilePath python -ArgumentList 'qemu-faults\qemu_launch_vm.py'
Start-Sleep -Seconds 5
Write-Output '[+] Running Mixed Read/Write workload...'
fio ..\spdk\fio_mixed_rw.job --output-format=json --output=..\reports\fio_guest.json
Write-Output '[+] Injecting random latency spikes...'
for ($i=0; $i -lt 5; $i++) {
    $delay = Get-Random -Minimum 50 -Maximum 200
    python qemu-faults\nbd_delay.py 10810 $delay
    Start-Sleep -Seconds (Get-Random -Minimum 5 -Maximum 20)
}
Write-Output '[+] Injecting power loss and recovery...'
for ($i=0; $i -lt 3; $i++) {
    python qemu-faults\qmp_injector.py --socket \\.\pipe\vm-test_qmp --action remove --device-id nvme0
    Start-Sleep -Seconds 10
    python qemu-faults\qmp_injector.py --socket \\.\pipe\vm-test_qmp --action add --device-spec '{"driver":"nvme","drive":"drive0","id":"nvme0"}'
    Start-Sleep -Seconds 30
}
Write-Output '[+] Running Behave for automated verification...'
behave --tags=@windows features/ssd_fault_injection.feature
Write-Output '[+] Test completed, shutting down VM...'
Stop-Process -Name qemu-system-x86_64 -Force