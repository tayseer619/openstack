#!/bin/bash

# RUN THIS BASH SCRIPT AS A USER WITH SUDOER PERMISSIONS, RUNNING AS ROOT IS NOT PREFERRED
# EXAMPLE:
# su - ansible
#
# NOTE THAT THE PYTHON VIRTUALENVIRONMENT THAT IS CREATED IS ALWAYS CALLED VENV
# YOU WILL ALSO BE ASKED TO LOG INTO THE ENTERPRISE GITHUB WHEN CLONING THE AUTOMATOS REPO
pass=$1
set_env() {
        echo "#################### Creating Env ####################"
    mkdir ~/.pip/
        printf "[global]\nindex-url = https://afeoscyc-mw.cec.lab.emc.com/artifactory/api/pypi/cyclone-pypi/simple/
        \nextra-index-url = https://pypi.python.org/simple/\ntrusted-host =  afeoscyc-mw.cec.lab.emc.com\n\tpypi.python.org
        " > ~/.pip/pip.conf
        sudo python3 -m pip install --upgrade pip
        sudo python3 -m pip install virtualenv virtualenvwrapper
        cd ~
        virtualenv venv
        source venv/bin/activate
        sudo dnf module install -y redis
        sudo systemctl start redis
        sudo systemctl enable redis
}

get_ini_file() {
	echo "#################### Getting Ini File ####################"
	      SAH_IP=$(cat ~/pilot/install-director.log | grep Permanently | cut -d ' ' -f 4 | head -1 | tr -d "'")
        IFS=. read -a ArrIP<<<"$SAH_IP"    
        name_of_inifile=/root/*${ArrIP[2]}.ini
        name_of_properties_file=/root/*${ArrIP[2]}.properties
        SAH_IP=root@$SAH_IP
        sshpass -p $pass scp -o StrictHostKeyChecking=no $SAH_IP:$name_of_inifile $HOME
        sshpass -p $pass scp -o StrictHostKeyChecking=no $SAH_IP:$name_of_properties_file $HOME
        echo "imported ini file and properties file"
  echo "################# Updating Bash profile ###################"
        echo "source ~/r${ArrIP[2]}rc" >> ~/.bash_profile
        echo "source ~/venv/bin/activate" >> ~/.bash_profile
        echo "Bash profile updated"
}

start_automatos() {
        echo "#################### Cloning Automatos ####################"
        cd ~
        export GIT_SSL_NO_VERIFY=true
        git clone -b openstack-testbed https://eos2git.cec.lab.emc.com/TSB-engineering/automatos
        echo "#################### Installing Automatos ####################"
        cd automatos/
        python3 bin/install_script.py -i
        pip install jinja2
        pip install pathlib
        pip install redfish==2.2.0
        pip install pexpect
        pip install configparser
        echo "#################### Installation Complete ####################"
        cd $pwd
        printf "\nNow start run_suite.\n"
}

pwd=$(pwd)
set_env
get_ini_file
start_automatos
