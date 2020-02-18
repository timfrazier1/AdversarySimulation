
# ATT&CK Simulator
This project provides a set of tooling for repeatedly executing and detecting adversary techniques.  This project uses the MITRE ATT&CK Enterprise techniques taxonomy (https://attack.mitre.org/techniques/enterprise/) and the MITRE ATT&CK navigator web app (https://github.com/mitre-attack/attack-navigator).  This project also makes extensive use of the Atomic Red Team project from Red Canary: (https://github.com/redcanaryco/atomic-red-team), Olaf Hartong's ThreatHunting App for Splunk: (https://github.com/olafhartong/ThreatHunting), Splunk Security Essentials App: (https://splunkbase.splunk.com/app/3435/) and my personal fork of Chris Long's DetectionLab project that includes Phantom in the Terraform scripts for easy spin up: (My Fork: https://github.com/timfrazier1/DetectionLab Original Project: https://github.com/clong/DetectionLab). Once set up, you will be able to repeatedly execute specific techniques, observe the resulting events in Splunk and refine your detection rules and methodology.  

Here is a short video demonstrating how it works and what it looks like once set up:

[![ATT&CK Sim Demo](https://i.vimeocdn.com/video/822348002.webp)](https://vimeo.com/366337885)


# ATT&CK Sim Install Guide
This guide is intended to provide a prescriptive path to getting a minimal adversary simulation setup using Splunk and Phantom (free/community editions).  There is obviously much left to the reader once the setup is complete in terms of what techniques to test.

There are a few ways to get this up and going.  If you have access to an AWS environment, **Option A will be your fastest and easiest path.**

- [Option A](https://github.com/timfrazier1/AdversarySimulation/wiki/Setup-Option-A): Spin up a fully isolated DetectionLab in AWS using Terraform (~45 minutes)
- [Option B](https://github.com/timfrazier1/AdversarySimulation/wiki/Setup-Option-B): Build your own AWS AMIs and configure manually (~a few hours)
- [Option C](https://github.com/timfrazier1/AdversarySimulation/wiki/Setup-Option-C): Use Detection Lab locally for getting the basic components in place and configure the rest manually (~a few hours)


## Workflow Example

After getting everything setup, here are instructions for a [workflow example.](https://github.com/timfrazier1/AdversarySimulation/wiki/Workflow-Example)

<br>
<br>
Alternate video link on YouTube:

[![ATT&CK Sim Demo](http://img.youtube.com/vi/jAMz18dTeMc/0.jpg)](https://www.youtube.com/watch?v=jAMz18dTeMc)
