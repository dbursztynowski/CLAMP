Scripts allowing one to trigger Nova resize command for changing the flavor of a server in OpenStack from Ansible playbook. 
Motivation: currently, OpenStack-related modules in Ansible do not support Nova RESIZE operation out of the box.

Description:

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
6. The complete set of scripts for operational adoption contains:
   - resize2m1.sh, resize2m1.sh that resize to m1large flavor and m2large flavor, respectively; both have to be stored on the remote agent
   - confirm.sh that (automatically in our case) confirms the resize operation to Nova as required by OpenStack (this includes timed chekout 
     introduced for "completeness"); called from resize2m1, resize2m2; stored on the remote agent
   - ansible-resize2m1.yml, ansible-resize2m2.yml are Ansible playboks used to trigger resizing to m1large and m2large flavor, respectively, 
     on a remote machine; both have to be stored on the Ansible server (in ONAP case, for the use of APPC or simlar module).