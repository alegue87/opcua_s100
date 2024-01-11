Place that file in your daemon service folder (usually /etc/systemd/system/), 
in a *.service file, and install it using the following systemctl commands 
(will likely require sudo privileges):

esempio di servizio avviato con: systemctl start s100. Con estenzione .service

[Unit]
Description = python opcua s100 server 
After = network.target # Assuming you want to start after network interfaces are made available
 
[Service]
Type = simple
ExecStart = /home/pii/dev/s100/opcua_s100/init.sh
User = pii 
# Group = # Group to run the script as
Restart = on-failure # Restart when there are errors
# SyslogIdentifier = <Name of logs for the service>
RestartSec = 5
TimeoutStartSec = infinity
 
[Install]
WantedBy = multi-user.target # Make it accessible to other users

