#!/usr/bin/python

import pexpect
import subprocess
import os
import time

# User plugs usbkey with USB storage device into PC
while True:
	# Only a USB storage device will have device name of sd*
	output = subprocess.check_output(('find', '/dev', '-name', 'sd*1'))
	if output:
		# Get the name of the device
		# For now assume that device is partitioned has only ONE partition
		print "attached"
		device = output.split('\n')[0]
		print device
		break
	else:
		print "not attached"
		time.sleep(1)

# Check if USB device is of filesystem type LUKS
blkid = subprocess.Popen(('blkid'), stdout=subprocess.PIPE)
output = subprocess.check_output(('grep', device), stdin=blkid.stdout)

output = output.split('\n')[0]
if output:
	print output
	# Get the TYPE of filesystem
	output = output.split(' ')[2]
	is_crypto_luks = 'crypto_LUKS' in output	

	# If LUKS, get passphrase from app
	if is_crypto_luks:
		print 'is_crypto_luks'
		# TODO: SEND SIGNAL TO APP TO GET PASSPHRASE
		passphrase = 'b'
                # Open the device's partition and setup a mapping name time.time()
                mapping_name = str(int(time.time()))
                #output = subprocess.check_output(('cryptsetup', 'luksOpen', device, mapping_name))
		child = pexpect.spawn('cryptsetup luksOpen ' + device + ' ' + mapping_name)
                child.expect('Enter passphrase for ' + device + ':')
                child.sendline(passphrase)
		# TODO work out what is the shortest timing that works...
		time.sleep(15)

	else:
		print 'not luks'
		# TODO: SEND SIGNAL TO APP TO GET NEW PASSPHRASE
		# This is a new storage device.
		passphrase = 'b'
		# Configure LUKS partition

		# Format storage device with NEW PASSPHRASE
		child = pexpect.spawn('cryptsetup luksFormat ' + device)
		child.expect('This will overwrite data on '+ device + ' irrevocably.')
		#child.expect('Are you sure? (Type uppercase yes): ')
		child.sendline('YES')
		child.expect('Enter LUKS passphrase:')
		child.sendline(passphrase)
		child.expect('Verify passphrase:')
		child.sendline(passphrase)
		time.sleep(5)
		
		# Open the device's partition and setup a mapping name time.time()
		mapping_name = str(int(time.time()))
		child = pexpect.spawn('cryptsetup luksOpen ' + device + ' ' + mapping_name)
		child.expect('Enter passphrase for ' + device + ':')
		child.sendline(passphrase)
		time.sleep(20)
		# Create a partition of the device
		output = subprocess.check_output(('mkfs.msdos', '/dev/mapper/' + mapping_name))
		time.sleep(20)
else:
	print "shouldn't happen"

# Activate the mass storage gadget driver
output = subprocess.check_output(('modprobe', 'g_mass_storage', 'file=/dev/mapper/' + mapping_name))

print 'real success'

# Check to see if app (mobile device) is within range
