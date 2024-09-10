# Setup QEMU Debian ARMHF
The below instructions might be used to setup a _QEMU Debian ARMHF_ virtual machine (VM).
## Installing
Install the _QEMU Debian ARMHF_ VM (here using Debian version 11.10, but more recent ones might be
used instead):
```shell
# Download Kernel and initial RAM disk
mkdir Debian-11.10-ARMHF && cd Debian-11.10-ARMHF/
wget http://http.us.debian.org/debian/dists/Debian11.10/main/installer-armhf/current/images/netboot/vmlinuz
wget http://http.us.debian.org/debian/dists/Debian11.10/main/installer-armhf/current/images/netboot/initrd.gz

# Install dependencies
sudo apt install qemu qemu-kvm qemu-system-arm libguestfs-tools

# Create disk image
qemu-img create -f qcow2 debian-11.10-armhf.qcow2 10G

# Install the system
qemu-system-arm -machine virt -m 1024 \
    -kernel vmlinuz \
    -initrd initrd.gz \
    -drive if=none,file=debian-11.10-armhf.qcow2,format=qcow2,id=hd \
    -device virtio-blk-device,drive=hd \
    -netdev user,id=mynet \
    -device virtio-net-device,netdev=mynet \
    -nographic -no-reboot
```
**Note**: Finish the installation without installing the _GRUB_ boot loader.
## Extracting the Kernel and Initial RAM Disk
Identify and extract the Kernel and initial RAM disk:
```shell
# Identify
sudo virt-ls -a debian-11.10-armhf.qcow2 /boot/
    # Output:
    #   System.map-5.10.0-30-armmp-lpae
    #   System.map-5.10.0-32-armmp-lpae
    #   config-5.10.0-30-armmp-lpae
    #   config-5.10.0-32-armmp-lpae
    #   initrd.img
    #   initrd.img-5.10.0-30-armmp-lpae
    #   initrd.img-5.10.0-32-armmp-lpae
    #   initrd.img.old
    #   lost+found
    #   vmlinuz
    #   vmlinuz-5.10.0-30-armmp-lpae
    #   vmlinuz-5.10.0-32-armmp-lpae
    #   vmlinuz.old

# Extract
sudo virt-copy-out -a debian-11.10-armhf.qcow2 \
    /boot/vmlinuz-5.10.0-32-armmp-lpae \
    /boot/initrd.img-5.10.0-32-armmp-lpae \
    .
```
## Running
Start the VM using a helper script:
```shell
# Create run script
cat << EOF > run.sh
#!/bin/bash
qemu-system-arm -machine virt -m 1024 \
-kernel vmlinuz-5.10.0-32-armmp-lpae \
-initrd initrd.img-5.10.0-32-armmp-lpae \
-append 'root=/dev/vda2' \
-drive if=none,file=debian-11.10-armhf.qcow2,format=qcow2,id=hd \
-device virtio-blk-device,drive=hd \
-netdev user,id=mynet,hostfwd=tcp::3000-:3000,hostfwd=tcp::3022-:22 \
-device virtio-net-device,netdev=mynet \
-nographic
EOF

# Make the script executable an run it
sudo chmod +x run.sh
./run.sh
```
## Configuring
Log in to the VM and perform the following configuration steps:
```shell
# Update system and install sudo
su -
apt update && apt full-upgrade -y
apt install sudo

# Add user to sudo group
usermod -aG sudo <USER>
su - <USER>

# Install gdbserver
sudo apt install -y gdbserver
```
----------------------------------------------------------------------------------------------------
[Back-to-Top](./1_setup_guest.md#setup-qemu-debian-armhf)