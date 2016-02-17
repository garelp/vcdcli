# vcdcli
Cli for Vmware VCloud Director.


## Requirement:
	1. HTTPie (apt-get install HTTPie)
	2. Requests (apt-get install python-requests)
	3. PrettyTable (apt-get install python-prettytable)
	

## Usage:
	usage: vcdcli.py [-h] [--login] [--list] [--poweron VAPPON]
	                 [--poweroff VAPPOFF] [--show OBJNAME] [--delete OBJTODELETE]
	                 [--shutdown VAPPSHUT] [--vdc VDCNAME]
	                 [--username VCLOUDUSERNAME] [--password VCLOUDPASSWORD]
	                 [--org VCLOUDORG] [--host VCLOUDHOST]
	                 [operation]

	positional arguments:
	  operation             vapp, template, pool ...

	optional arguments:
	  -h, --help            show this help message and exit
	  --login               login with new credentials
	  --list                list data
	  --poweron VAPPON      Power on Vapp
	  --poweroff VAPPOFF    Power off Vapp
	  --show OBJNAME        show object
	  --delete OBJTODELETE  delete object
	  --shutdown VAPPSHUT   Shutdown vapp
	  --vdc VDCNAME         select specific pool
	  --username VCLOUDUSERNAME
	                        VCloud username
	  --password VCLOUDPASSWORD
	                        VCloud password
	  --org VCLOUDORG       VCloud Organisation
	  --host VCLOUDHOST     VCloud host
  