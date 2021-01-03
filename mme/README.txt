This folder contains the files related to the event logger part of wef-agent server.

The following files are used actively in the demo (remaining files serve testing purposes
and are not necessary to run the demo):

* event-logger.sh - the main script, to be run manually to start a logging session; 
  it has an optional parameter with possible value -v to indicate a detailed level
  of the output from executing curl commands (bo basic purposes leave it blank). 
  The script periodically (every 2 min.) downloads the statistisc' log from the MME VM using 
  curl and stores it in the file mme-clamp.log. It then executes Python script VESprepareSendEvent.py
  that reads mme-clamp.log, formats the telemetry event and stores it for sending in
  file VES_send_event.json. event-logger.sh then sends VES_send_event.json to VES collector using curl.

  Note: use optional parameter -v (./event-logger.sh -v) for a detailed curl uutput.

* VESprepareSendEvent.py - invoked by event-logger.sh, is a Python script that prepares the telemetry
  event to be sent to VES based on the contents of file mme-clamp.log and using file 
  VES_send_template.json as template for VES event format. It then stores the prepared event in file
  VES_send_event.json.

* VES_send_template.json - used by VESprepareSendEvent.py as the template for VES telemetry event.

* VES_send_event.json - produced by VESprepareSendEvent.py, send by event-logger.sh to VES collector,
  contains MME VM event to be sent directly to VES collector. 
