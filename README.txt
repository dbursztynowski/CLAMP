Note: only the files explicitly mentioned here are operationally valid. Remaining files are not needed for 
running the demo.

Scripts allowing one to trigger Nova resize command for changing the flavor of a server in OpenStack 
Initially, they were created to be called form Ansible playbook (and are ready for that). In current 
demo version, they are called by Python script policy-enf.py that is a simplistic (used only in this demo) 
by-pass of APPC

Note: Currently, OpenStack-related modules in Ansible do not support Nova RESIZE operation out of the box. This
is the reason why in case of Ansible we use scripts of the type provided here.

Currently The main loop is provided by Python script policy-enf.py. It can be thought of as a module implementing policy 
enforcmenet point that catches the requests for ModifyConfig operation sent by the Policy framework (PDP-D) on 
topic APPC-CL (APPC closed loop). The process running policy-enf.py sniffs on APPC-CL topic and once 
ModifyConfig operation is catched, it makes a simple format check, extract resize parameter form it, converst
its value to respective OpenStack VM flavor name and calls shell script 
Currently The main loop is provided by Python script policy-enf.py. It can be thought of as a module implementing policy
enforcmenet point that catches the requests for ModifyConfig operation sent by the Policy framework (PDP-D) on
topic APPC-CL (APPC closed loop). The process running policy-enf.py sniffs on APPC-CL topic and once                                                                                                             ModifyConfig operation is catched, it makes a simple format check, extract resize parameter form it, converst                                                                                                    its value to respective OpenStack VM flavor name and calls shell script

Description of OpenStack-related scripts in case of using Ansible
=================================================================

1. Resizing scripts are shell scripts that have to be stored on a dedicated machine (remote agent) that has installed OpenStack command 
   line tools. OpenStack command tools commands are called from such shell scripts. Each schell script contains directives from openrc.sh 
   file (copied form OpenStack) so they are expected to be self-sufficient, i.e., sourcing openrc.sh separately should not be needed 
   (although it does not make any harm if sourced). 
2. Resizing scripts are triggered remotely from Ansible playbooks using Ansible shell module (ansible.builtin.shell). In the playbooks, they 
   are referred to as bash executables (see "executable: /bin/bash" in the the playbook code).
3. Each resize script (in this examplary set there are two such scripts) resizes the machine to a specific flavor (resize2m1 resizes to 
   m1large flavor, resize2m2 resizes to m2large flavor). The correctness of such a call is up to the requersting entity (e.g., resizing to the same 
   flavor fails with notification, resizing to flavor with different disk size(s) fails withoput notification - nothing happens). The scripts 
   provide only basic exception handling. In practice, the specific set of flavors to be used should be tailored to the use case.
4. Certain execution progress information is written to log files (one file being local to Ansible server, the same folder as theAnsible 
   playbook, and one on the remote agent, the same folder as the remote shell scripts).
5. All case-specific data (directories, machine name(s), user accounts, etc.) have to be adopted appropriately.
6. The complete set of scripts for the operational adoption contains:
   - resize2m1.sh, resize2m1.sh that resize to m1large flavor and m2large flavor, respectively; both have to be stored on the remote agent
   - confirm.sh that (automatically in our case) confirms the resize operation to Nova as required by OpenStack (this includes timed chekout 
     introduced for "completeness"); called from resize2m1, resize2m2; stored on the remote agent
   - ansible-resize2m1.yml, ansible-resize2m2.yml are Ansible playboks used to trigger resizing to m1large and m2large flavor, respectively, 
     on a remote machine; both have to be stored on the Ansible server (in ONAP case, for the use of APPC or simlar module).
Note: if Ansible triggering will be deployed, scripts resize2m1 and resize2m2 will probalby by substituted by parametrized use of resize.sh
described below for the case of using policy-enf.py. However, the use of Ansible-Server facility that is needed by APPC may demand changing 
some details of the scripts - this is TBD.

Description for the case of using policy-enf.py:
================================================

1. Currently, ONAP module APPC is not used in the demo, and the events on APPC-CL topic in DCAE/DMaaP 
(including those sent by Policy) are sniffed by Python script policy-enf.py. It can be thought of as a 
module implementing the policy enforcement point function that catches the requests for ModifyConfig 
operation sent by the Policy framework (PDP-D) on topic APPC-CL (APPC closed loop). The process running 
policy-enf.py sniffs on APPC-CL topic and once ModifyConfig operation is catched, it makes a simple 
format check, extracts the value of the resize parameter form it (4 or 6 - inherited fromm the vFW 
use case), converts its value to the respective OpenStack VM flavor name (in our case, 4 from Policy 
means m1.large while 6 from Policy means m2.large) and calls shell script resize.sh that triggers the 
actual resize operation on the VM using OpenStack command line tool commands. policy-enf.py takes one 
optional parameter with allowed values -v, -vv, -vvv to indicate the required level od detail in 
ouput for diagnostic purposes. For basic demoing, -v is the recommended value ($ python3 policy-enf.py -v).

2. resize.sh - called by policy-enf.py, triggers a chain of calls to OpenStack command line tool commands;
uses another script confirm.sh that handles the procedure of veryfying and conforming the resize operation 
to Nova including basic exception handling. It accepts two required parameters: OpenStack name of the VM to 
resize and the flavor (valid OpenStackt string) to which the VM is to be resized.

3. confirm.sh - similar role as described above for the case of Ansible.
