#!/usr/bin/python
import sys
import json
import base64
import requests
import time

try:
    session_password = sys.argv[1]
except:
    session_password = 'password'

def install_app(full_filepath):

    file_contents = open(full_filepath, 'rb').read()
    encoded_contents = base64.b64encode(file_contents)
    payload = {'app': encoded_contents}
    r = requests.post('https://192.168.38.110/rest/app',
                auth=('admin', session_password),
                data=json.dumps(payload),
                verify=False)
    print r.status_code
    print r.text

install_app('/opt/AdversarySimulation/resources/phantom_apps/phatomicredteam.tgz')
install_app('/opt/AdversarySimulation/resources/phantom_apps/phwinrm.tgz')
install_app('/opt/AdversarySimulation/resources/phantom_apps/phscythe.tgz')

try:
    s = requests.Session()
    s.verify = False
    s.auth = ('admin', session_password)
except Exception as e:
    print "Session set up failed: " + str(e)

# Get session cookies
try:
    s.get('https://localhost/login')
except Exception as e:
    print "Unable to get session cookie: " + str(e)

# Update playbook repository
try:
    data = {"uri": "https://github.com/timfrazier1/AdvSimPlaybooks.git", 
            "name": "AdvSim",
            "branch": "master",
            "repo-user": "",
            "repo-pass": "",
            "read_only": "on",
            "save": "true"}
    repo_resp = s.post('https://localhost/scm/', data)
    print repo_resp.text
except Exception as e:
    print "Unable to create playbook repo: " + str(e)

# Grab token
try:
    token_response = s.get('https://localhost/rest/ph_user/2/token')
    token = token_response.json()['key']
    print "Token grabbed: " + str(token)
except Exception as e:
    print "Unable to get token for automation user: " + str(e)

# Update automation user
try:
    s.post('https://localhost/rest/ph_user/2', json={"allowed_ips": ["any"], "default_label": "advsim_test"})
except Exception as e:
    print "Unable to update allowed IPs to any: " + str(e)

try:
    s.post('https://localhost/rest/asset', json={"configuration": {"verify_cert": True,
    "base_url": "https://github.com/redcanaryco/atomic-red-team.git"},
    "name": "art_main_repo", "product_name": "Atomic Red Team",
    "product_vendor": "Red Canary"})
except Exception as e:
    print "ART asset POST failed: " + str(e)
try:
    s.post('https://localhost/rest/container', json={"label": "events", "name": "Example Container"})
except Exception as e:
    print "Example container POST failed: " + str(e)
try:
    art_app_response = s.get('https://localhost/rest/app?_filter_name__contains=%22Atomic%22')
    art_app_id = art_app_response.json()['data'][0]['id']
except Exception as e:
    print "Get ART App ID failed: " + str(e)

#f = open("app_id.txt", "w")
#f.write(app_response.json['data'][0]['id'])
#f.close()
try:
    s.post('https://localhost/rest/action_run', json={"action": "test connectivity", "container_id": 1, "name": "art_test_connectivity", "targets": [{"assets": ["art_main_repo"], "parameters": [], "app_id": art_app_id}]})
except Exception as e:
    print "Run ART test connectivity action failed: " + str(e)

print "\nSleeping for two minutes... \n"
time.sleep(120)
try:
    s.post('https://localhost/rest/asset', json={"name": "winrm_dect_lab", "product_name": "Windows Remote Management", "product_vendor": "Microsoft", "configuration": {"username": "vagrant", "domain": "", "endpoint": "192.168.38.104", "verify_server_cert": False, "default_port": "5985", "default_protocol": "http", "password": "vagrant", "transport": "ntlm"}})
    s.post('https://localhost/rest/asset', json={"name": "splunk_dect_lab", "product_vendor": "Splunk Inc.", "product_name": "Splunk Enterprise", "configuration": {"username": "admin", "max_container": 100, "ingest": {"container_label": "splunk_events", "start_time_epoch_utc": ""}, "retry_count": "3", "verify_server_cert": False, "device": "192.168.38.105", "timezone": "UTC", "password": "changeme", "port": "8089"}})
    s.post('https://localhost/rest/asset', json={"name": "dect_lab_logger", "product_vendor": "Generic", "product_name": "SSH", "configuration": {"username": "vagrant", "password": "vagrant", "root": False, "test_device": "192.168.38.105"}})
except Exception as e:
    print "POST assets failed: " + str(e)

try:
    repo_response = s.get('https://localhost/rest/scm?_filter_name=%22AdvSim%22')
    repo_id = repo_response.json()['data'][0]['id']

    s.post('https://localhost/rest/scm/' + str(repo_id), json= {"pull": True, "force": True})
except Exception as e:
    print "GET and POST repo info failed: " + str(e)

try:
    playbook_response = s.get('https://localhost/rest/playbook?_filter_name=%22Modular%20Simulation%22')
    playbook_id = playbook_response.json()['data'][0]['id']

    s.post('https://localhost/rest/playbook/' + str(playbook_id), json = {"active": True, "cancel_runs": True})
except Exception as e:
    print "GET and POST playbook info failed: " + str(e)


try:
    winrm_app_response = s.get('https://localhost/rest/app?_filter_name__contains=%22Remote%22')
    winrm_app_id = winrm_app_response.json()['data'][0]['id']
except Exception as e:
    print "Get WinRM App ID failed: " + str(e)
try:
    s.post('https://localhost/rest/action_run', json={"action": "run script", "container_id": 1,
        "name": "install powershell modules", "targets": [{"assets": ["winrm_dect_lab"],
        "parameters": [{
            "async": False,
            "script_str": "Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force; Install-Module -Name powershell-yaml -Scope CurrentUser -Force",
            "ip_hostname": "192.168.38.104"}],
        "app_id": winrm_app_id}]})
except Exception as e:
    print "Run Win RM install powershell modules failed: " + str(e)
