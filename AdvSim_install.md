
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
11. Will need to make sure the lookup for attck_assets is correct, either using "Lookup Editor" Splunk app or manually editing.


### Setting up Phantom:
1. Launch Splunk Phantom AMI on AWS (or on-prem)
2. Login with admin/password  (You should change your password)
3. Go to Administration --> User Management --> Users
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

### Phantom SSH to set up certificate
1. Run the following as root:
```
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum install -y certbot python2-certbot-nginx python2-certbot-dns-google
certbot --nginx certonly
#Feed in your domain name and then cd to the new directory with the certs once Created
cp /opt/phantom/etc/ssl/certs/httpd_cert.crt /opt/phantom/etc/ssl/certs/httpd_cert.crt.bak
cp fullchain.pem /opt/phantom/etc/ssl/certs/httpd_cert.crt
cp /opt/phantom/etc/ssl/private/httpd_cert.key /opt/phantom/etc/ssl/private/httpd_cert.key.bak
cp privkey.pem /opt/phantom/etc/ssl/private/httpd_cert.key
service nginx reload
```

FYI: to renew certificate at a later date, simply run:
```
certbot renew
cp <path_to_new_cert>/fullchain.pem /opt/phantom/etc/ssl/certs/httpd_cert.crt
cp <path_to_new_cert>/privkey.pem /opt/phantom/etc/ssl/private/httpd_cert.key
service nginx reload
```

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
    - Using these instructions: https://www.visualstudiogeeks.com/devops/how-to-configure-winrm-for-https-manually
    - In powershell:
    ```
    winrm quickconfig
    New-SelfSignedCertificate -DnsName "<YOUR_DNS_NAME>" -CertStoreLocation Cert:\LocalMachine\My
    winrm create winrm/config/Listener?Address=*+Transport=HTTPS '@{Hostname="<YOUR_DNS_NAME>"; CertificateThumbprint="<COPIED_CERTIFICATE_THUMBPRINT>"}'
    # Add a new firewall rule
    port=5986
    netsh advfirewall firewall add rule name="Windows Remote Management (HTTPS-In)" dir=in action=allow protocol=TCP localport=$port
    ```
    - Open port 5986 inbound on AWS for Server (sometimes this is already present)

    To review WinRM config:
    ```
    winrm get winrm/config -format:pretty
    ```

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


## Option 2: Spin up Detetion Lab
  1. Follow instructions here to spin up DetectionLab: https://github.com/clong/DetectionLab
  2. From the console for "logger" vm (or via ssh):
  ```
  su splunk
  cd /opt/splunk/etc/apps
  git clone https://github.com/daveherrald/SA-attck_nav.git
  git clone https://github.com/daveherrald/SA-advsim.git
  ```
  3. From the UI, Navigate to "Administrator" --> "Account Settings"
  4. Change Administrator password to a new value
  5. From the UI, navigate to "Apps" --> "Find More Apps"
    - Search for "Phantom" and install "Phantom App for Splunk"
    - Search for "lookup" and install "Lookup File Editor"
    - Search for "CIM" and install "Splunk Common Information Model (CIM)"
    - Install Base64 app from Splunkbase: https://splunkbase.splunk.com/app/1922/
    - Then restart Splunk
  7. From the UI, navigate to "Settings" --> "Access Controls"
  8. Click "Roles", then "admin"
  9. Under the "inheritance" section, add the "phantom" role.  
  10. Scroll down and click "save" at the bottom.
  11. Unless you have a valid certificate for Phantom, you will need to disable certificate validation by running:
  ```
  curl -ku 'username:password' https://<splunk-address>:8089/servicesNS/nobody/phantom/configs/conf-phantom/verify_certs\?output_mode\=json -d value=0
  ```
   - with the appropriate substitutions, of course
   - CAVEAT EMPTOR: Disabling certificate checking is not allowed in Splunk Cloud and does make the setup less secure.

  10. Create the "security" index if using the inputs.conf below
  11. Will need to make sure the lookup for attck_assets is correct, either using "Lookup Editor" Splunk app or manually editing.

    - Go to Apps --> Lookup Editor
    - Under the "Lookups" title and to the right, click on the filter labeled "App: All" and select "Adversary Simulator"
    - Click the only lookup there, "attck_assets.csv"
    - Adjust these lines to match your environment

  14. Modify the file `/opt/splunk/etc/apps/phantom/bin/ta_addonphantom/modalert_phantom_forward_helper.py`
    - Comment out the "return results" line and uncomment the "return 0" line

### Setting up Phantom:
  1. Launch Splunk Phantom AMI on AWS (or on-prem)
  2. Login with admin/password  (You should change your password)
  3. Go to Administration --> User Management --> Users
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

### Back in Phantom:
  (Assumption is that the Phantom VM has internet connectivity to download Atomic Red Team)
- Setting up Win RM
  1. Go to Apps from the main menu
  2. Search for "Windows" and find the Windows Remote Management app under unconfigured Apps
  3. Click "Configure New Asset" on the right hand side and give the asset a name while in the "Asset Info" tab
  4. Under "Asset Settings", point to your Win Server hostname for test connectivity
  5. For AWS Windows box following above Windows Setup:
    - Use HTTPS as default protocol and change port to 5986
    - Leave domain blank
    - Use NTLM transport and input your admin user and password
  6. For DetectionLab Windows box:
    - Use the Win10 box IP address for testing
    - Use HTTP as default protocol and leave port as 5985
    - Use WIN10 as the domain
    - Use NTLM transport and input "vagrant" user and "vagrant" password
  7. Save and "Test connectivity" to validate
- Setting up Splunk connectivity from Phantom
  1. From main menu, go to Apps
  2. Search for "Splunk" and click on "unconfigured apps" to find it
  3. Click "Configure new asset" on the right hand side
  4. Give it a name with no spaces under "asset info" then click "asset settings" tab
  5. Put in the IP/Hostname, username and password for your Splunk instance
  6. Change the timezone to UTC (unless you have this set differently in Splunk)
  7. Go to the Ingest Settings tab and select (or define) a label to assign to the inbound Splunk events
  8. Click "Save" go back to the "Asset Settings" tab and then click "Test Connectivity" at the bottom to validate that it is working
- Setting up Atomic Red Team app
  1. Download https://github.com/timfrazier1/AdversarySimulation/blob/master/phatomicredteam.tgz
  2. Go to Apps from the main menu
  3. Click the "Install App" button in the upper right
  4. Select the downloaded "phatomicredteam.tgz" file
  5. Once app is installed, find "Atomic Red Team" in unconfigured Apps
  6. Click "Configure new Asset" on the right hand side
  7. Paste in https://github.com/redcanaryco/atomic-red-team.git if you want to use the main ART repo, otherwise, use your own fork
  8. Hit "Save" and then "Test Connectivity" to build the list of tests
  9. You should see a "Repo Created Successfully" message
- Setting up the Playbook
  1. From the main menu, go to Administration -> Administration Settings -> Source Control
  2. Select "configure new repository", then paste https://github.com/daveherrald/AdvSim into the URL field
  3. Use "AdvSim" as the name and "master" as the branch
  4. Check the "read-only" box and click "Save"
  5. From the main menu, go to "Playbooks"
  6. On the listing screen, click the "Repo" column and select "AdvSim" to see the playbooks associated with the repo
  7. Click on "Modular Simulation" to view the playbook in the editor
