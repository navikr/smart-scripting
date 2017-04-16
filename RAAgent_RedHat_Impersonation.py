import os

def createGrp():
        print("Creating group deployerGrp")
        os.system("groupadd deployerGrp")
        groupDetails=os.popen("getent group deployerGrp")
        groupId=(groupDetails.read()).split(':')[2]
        print("deployerGrp id:",groupId)
        return groupId

def createUsers(groupId):
        print("creating users")
        exeCmd="useradd -m -g {} test1 -p test1@123".format(str(groupId))
        print("executing command: "+exeCmd)
        os.system(exeCmd)
        exeCmd="useradd -m -g {} test2 -p test2@123".format(str(groupId))
        print("executing command: "+exeCmd)
        os.system(exeCmd)

def backsudoers():
        if os.path.isfile("/etc/sudoers"):
		lookup="root\tALL="
                with open("/etc/sudoers") as myfile:
                        for num, line in enumerate(myfile,1):
                                with open("/etc/sudoersnew",'a') as mynewfile:
                                        mynewfile.write(line)
                                        if lookup in line:
                                                mynewfile.write("test1\tALL=(test2) NOPASSWD:ALL")
						mynewfile.write("\n")
						mynewfile.write("test2\tALL=(test1) NOPASSWD:ALL")
                print("creating backup of /etc/sudoers")
                os.system("mv /etc/sudoers /etc/sudoers_bkpauto")
                os.system("mv /etc/sudoersnew /etc/sudoers")
		os.system("chmod 0440 /etc/sudoers")
        else:
                print("File /etc/sudoers doesn't exist")

def createUserFile():
	os.system("mkdir /tmp/test1")
	os.system("mkdir /tmp/test2")
	os.system("echo 'test file created by test1 accessible only by test1' > /tmp/test1/test1.txt")
	os.system("echo 'test file created by test2 accessible only by test2' > /tmp/test2/test2.txt")
	os.system("chmod 600 /tmp/test1/test1.txt")
	os.system("chmod 600 /tmp/test2/test2.txt")
	os.system("chown -R test1:deployerGrp /tmp/test1")
	os.system("chown -R test2:deployerGrp /tmp/test2")

def createCustomActionRunner(nolioAgentDir):
	exeCmd="echo 'echo \"nolio_password\" | sudo -u $3 -S ./ActionsRunner.sh $1 $2 $3' >{}/customActionsRunner.sh".format(nolioAgentDir)
	print("executing command : "+exeCmd)
	os.system(exeCmd)
	print("customActionsRunner.sh file created at path : {}/".format(nolioAgentDir))
	print("baking up process.properties and making suoders entry")
	processPropFile=nolioAgentDir+"/conf/processes.properties"
	processBkpFile=nolioAgentDir+"/conf/processes.properties_bkp"
	if os.path.isfile(processPropFile):
                lookup="cmd.to.execute="
                with open(processPropFile) as myfile:
                        for num, line in enumerate(myfile,1):
                                with open(processBkpFile,'a') as mynewfile:
                                        if lookup in line:
                                                mynewfile.write("cmd.to.execute={}/customActionsRunner.sh".format(nolioAgentDir))
					else:
						mynewfile.write(line+"\n")
                print("creating backup of {}".format(processPropFile))
		exeCmd="mv {} {}/conf/processesBKP.properties".format(processPropFile,nolioAgentDir)
                os.system(exeCmd)
		print("creating modified processes.properties file")
		exeCmd="mv {} {}".format(processBkpFile,processPropFile)
                os.system(exeCmd)
        else:
                print("File {}/conf/processes.properties  doesn't exist".format(nolioAgentDir))
def changeRunAsUser(nolioAgentDir):
	deployerConFile="{}/conf/deployer_configuration.sh".format(nolioAgentDir)
	deployerBKPFile="{}/conf/deployer_configuration.sh_bkp".format(nolioAgentDir)
	if os.path.isfile(deployerConFile):
                lookup="RUN_AS_USER="
                with open(deployerConFile) as myfile:
                        for num, line in enumerate(myfile,1):
                                with open(deployerBKPFile,'a') as mynewfile:
                                        if lookup in line:
                                                mynewfile.write("RUN_AS_USER=test1")
                                        else:
                                                mynewfile.write(line)
                print("creating backup of {}".format(deployerConFile))
                exeCmd="mv {} {}/conf/deployer_configuration.shBKP".format(deployerConFile,nolioAgentDir)
                os.system(exeCmd)
                print("creating modified processes.properties file")
                exeCmd="mv {} {}".format(deployerBKPFile,deployerConFile)
                os.system(exeCmd)
        else:
                print("File {}/conf/deployer_configuration.sh  doesn't exist".format(nolioAgentDir))
def changeNagDirPermission(nolioAgentDir):
	exeCmd="sh {}/deployer_daemon.sh remove".format(nolioAgentDir)
	os.system(exeCmd)
	exeCmd="chown -R test1:deployerGrp {}".format(nolioAgentDir)
	os.system(exeCmd)
	exeCmd="sh {}/deployer_daemon.sh install".format(nolioAgentDir)
	os.system(exeCmd)
	exeCmd="chmod 711 {}/customActionsRunner.sh".format(nolioAgentDir)
	os.system(exeCmd)
nolioAgentDir=raw_input("Enter Nolio Agent Directory [eg. /opt/ReleaseAutomationServer/NolioAgent]: ")

groupId=createGrp()
print("gropu details are", groupId)
createUsers(groupId)
backsudoers()
createUserFile()
createCustomActionRunner(nolioAgentDir)
changeRunAsUser(nolioAgentDir)
changeNagDirPermission(nolioAgentDir)
print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------")
print("1- User created: test1/test1@123 test2/test2@123						    									")
print("2- User Group created: deployerGrp                                                            									")
print("3- User Files created at /tmp/test1/test1.txt  & /tmp/test2/test2.txt                         									")
print("4- NolioAgent directory owner : test1:deployerGrp                                             									")
print("5- customActionsRunner.sh at location {}                                                      									".format(nolioAgentDir))
print("6- processes.properties backed up at location {}/conf with name processesBKP.properties       									".format(nolioAgentDir))
print("7- /etc/sudoers file backed up at location /etc/sudoers_bkpauto                               									")
print("NOTE: Please loging as test1 and restart the Nolio Agent Service                                                                                                 ")
print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------")

