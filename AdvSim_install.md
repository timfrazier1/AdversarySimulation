
# AdvSim Install Guide
This guide is intended to provide a prescriptive path to getting a minimal adversary simulation setup using Splunk and Phantom (free/community editions).  There is obviously much left to the reader once the setup is complete in terms of what techniques to test

### Setting up Splunk:

1. Launch Splunk Enterprise AMI on AWS (or on-prem version)
2. Commands from Splunk instance CLI
```
sudo su
yum install git -y
su splunk
cd /opt/splunk/etc/apps
git clone https://github.com/daveherrald/SA-attck_nav.git
git clone https://github.com/daveherrald/SA-advsim.git
/opt/splunk/bin/splunk restart
```

3. In the UI, navigate to _Settings_ > _Forwarding and Receiving_
  - Click _Add new_ under _Receiving_
  - Enter port 9997 and click _Save_
4. In the UI, click Settings > Monitoring Console.
  - From the app navigation menu, click Settings > General Setup.
  - Verify the server name and note the discovered default server roles.
  - Click Edit > Edit Server Roles.
  - Remove the check mark from Search Head (if present) and select Deployment Server, then click Save > Done.
  - To complete the app setup, click Apply Changes > Go to Overview.

5. From the UI, navigate to "Apps" --> "Find More Apps"
6. Search for "Phantom" and install the 3 apps found
7. Restart Splunk after installing all 3
8. Unless you have a valid certificate for Phantom, you will need to disable certificate validation by running:
```
curl -ku 'username:password' https://splunk:8089/servicesNS/nobody/phantom/configs/conf-phantom/verify_certs\?output_mode\=json -d value=0
```
 - with the appropriate substitutions, of course
 - CAVEAT EMPTOR: Disabling certificate checking is not allowed in Splunk Cloud and does make the setup less secure.
9. Need to download and install Sysmon-TA from Splunkbase: https://splunkbase.splunk.com/app/1914/
10. Create the "security" index if using the inputs.conf below


### Setting up Phantom:
1. Launch Splunk Phantom AMI on AWS (or on-prem)
2. Login with admin/password
3. Go to Administration --> User Management
4. Click on "automation" User
5. Change "Allowed IPs" to "any" (or appropriate subnet, if you prefer to be more secure)
6. Copy everything in the "Authorization Configuration for REST API" section
7. Click "Save"

Go back to Splunk:
1. Navigate to Apps --> Phantom --> Phantom Server Configuration
2. Click "Create Server"
3. Paste clipboard into "Authorization Configuration"
4. Give it a name (such as Phantom AWS)
5. Click "Save"
 - If something is wrong, you will get an error here

### At this point, you have the basic Splunk/Phantom setup

We will next need to get the Phantom app on Splunk set up



### For Windows Server 2019:
  1. Stand up AWS AMI for Windows Server 2019 Base
  2. Download and modify swiftonsecurity sysmon-config:
    - Key exclusions of splunk processes under process creation:
      - ```<Image condition="is">C:\Program Files\Splunk\bin\btool.exe</Image>
        <Image condition="is">C:\Program Files\Splunk\bin\splunkd.exe</Image>
        <Image condition="is">C:\Program Files\SplunkUniversalForwarder\bin\splunk-winprintmon.exe</Image>
        <Image condition="is">C:\Program Files\SplunkUniversalForwarder\bin\splunk-powershell.exe</Image>
        <ParentImage condition="is">C:\Program Files\SplunkUniversalForwarder\bin\splunkd.exe</ParentImage>
        ```
    - ~~Key inclusion for Mimikatz:~~
      - ~~<TargetImage condition="is">C:\windows\system32\lsass.exe</TargetImage>~~

  3. Download and install sysmon:
    https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon
    ```
    .\Sysmon.exe -accepteula -i .\sysmonconfig-export.xml
    ```

  4. Enable powershell logging to match settings at: https://www.fireeye.com/blog/threat-research/2016/02/greater_visibilityt.html

  5. Download and install Splunk Universal Forwarder:
    https://www.splunk.com/en_us/download/universal-forwarder.html
  6. Install Universal Forwarder as local system (accept defaults)
    - create local admin splunk_svc_acct
    - point to Splunk AWS Box IP as indexer (enter default port)
  7. Modify inputs.conf to include:
  ```
# Windows platform specific input processor.
[WinEventLog://Application]
disabled = 0
index = security
[WinEventLog://Security]
disabled = 0
index = security
[WinEventLog://System]
disabled = 0
index = security

  [WinEventLog://Microsoft-Windows-TaskScheduler/Operational]
  disabled = 0
  index = security

  [WinEventLog://Microsoft-Windows-WinRM/Operational]
  disabled = 0
  index = security

  [WinEventLog://Microsoft-Windows-Sysmon/Operational]
  disabled = 0
  renderXml = true
  index = security

  [WinEventLog://Microsoft-Windows-PowerShell/Operational]
  disabled = 0
  index = security
  blacklist1 = 4105,4106
  blacklist2 = EventCode="4103" Message="(?:SplunkUniversalForwarder\\bin\\splunk-powershell.ps1)"

  [monitor://C:\var\log\transcripts\]
  disabled = false
  index = security
  sourcetype = powershell_transcript
 ```
  8. Turn on WinRM service:
    - In powershell:
    ```
    winrm quickconfig
    New-SelfSignedCertificate -DnsName "<YOUR_DNS_NAME>" -CertStoreLocation Cert:\LocalMachine\My
    winrm create winrm/config/Listener?Address=*+Transport=HTTPS '@{Hostname="<YOUR_DNS_NAME>"; CertificateThumbprint="<COPIED_CERTIFICATE_THUMBPRINT>"}'
    # Add a new firewall rule
    port=5986
    netsh advfirewall firewall add rule name="Windows Remote Management (HTTPS-In)" dir=in action=allow protocol=TCP localport=$port
    ```
    - Allow port 5986 inbound through Windows Firewall
    - Open port 5986 inbound on AWS for Server (sometimes this is already present)

    To review WinRM config:
    ```
    winrm get winrm/config -format:pretty
    ```

### Back in Phantom:
  1. Go to Apps
  2. Search for "Windows" and find the Windows Remote Management app under unconfigured Apps
  3. Point to your Win Server hostname for test connectivity
  4. Use HTTPS as default protocol and change port to 5986
  5. Use NTLM transport and input your admin user and password
  6. Save and "Test connectivity" to validate

  




### For Windows 10:
  1. Stand up AWS Workspaces windows 10 box
  2. Download and install Splunk Universal Forwarder:
    https://www.splunk.com/en_us/download/universal-forwarder.html
  3. Install Universal Forwarder as local system (accept defaults)
    - create local admin splunk_svc_acct
    - ~~point to Splunk AWS Box IP as deployment Server (enter default port)~~
    - point to Splunk AWS Box IP as indexer (enter default port)
    -
  4. Download and modify swiftonsecurity sysmon-config:
    - Key exclusions of splunk processes:
      - ```<Image condition="is">C:\Program Files\Splunk\bin\btool.exe</Image>
        <Image condition="is">C:\Program Files\Splunk\bin\splunkd.exe</Image>
        ```
    - Key inclusion for Mimikatz:
      - ```<TargetImage condition="is">C:\windows\system32\lsass.exe</TargetImage>```

  5. Download and install sysmon:
    https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon
    ```
    sysmon.exe -accepteula -i sysmonconfig-export.xml
    ```
