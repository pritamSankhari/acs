
import os
import sys
import time
import json
import mysql.connector
from datetime import datetime
import shutil


# Accessing command-line arguments
arguments = sys.argv
if(len(arguments) <= 1):
	print('No Argument At All')
	sys.exit()
scriptID = arguments[1]


def decrypt12(text):
	d = ""
	for ch in text:
		d += chr(ord(ch)+12)
	return d	

def log_error(log,error):
	# Get the current date and time
	current_datetime = datetime.now()
	formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

	sql = f"INSERT INTO logs(logs,error,created_at) VALUES('{log}','{error}','{formatted_datetime}')"
	cursor.execute(sql)
	connection.commit()

def stop_script():
	sql = f"UPDATE scripts SET running_status=0 WHERE id={scriptID}"
	cursor.execute(sql)
	connection.commit()
	connection.close()

def backup(src_server,src_path,src_user,src_pass,dst_server,dst_path,dst_user,dst_pass,src_alias,dst_alias):
	try:
		os.system(f'net use {src_alias}: \\\\{src_server}\\{src_path}\\ /user:{src_user} {src_pass}')
		os.system(f'net use {dst_alias}: \\\\{dst_server}\\{dst_path}\\ /user:{dst_user} {dst_pass}')
		os.system(f'xcopy {src_alias}: Y: /E /I /H /K /Y')
		os.system(f'net use {src_alias}: /delete')
		os.system(f'net use {dst_alias}: /delete')
		log_error(f'Script ID:{scriptID} Backup Done','Successfully Done')
	except e:
		log_error('scriptID','Failed To Copy')
		stop_script()
		sys.exit()


def copy_all(src, dst):

	try:
	    if not os.path.exists(dst):
	        os.makedirs(dst)
	    for item in os.listdir(src):
	        s = os.path.join(src, item)
	        d = os.path.join(dst, item)
	        if os.path.isdir(s):
	            shutil.copytree(s, d, dirs_exist_ok=True)
	        else:
	            shutil.copy2(s, d)
	except:   
		log_error(f'Script ID:{scriptID} Error','Script closed uncertainly')        
		stop_script()


# Open the JSON file
with open('db-config.json', 'r') as file:
	# Load JSON data
	dbData = json.load(file)


current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

# os.system('net use X: \\\\192.168.5.234\\Linux_map\\map_one\\ /user:Dev1 Spl@222')
# os.system('net use Y: \\\\192.168.5.234\\Linux_map\\map_two\\ /user:Dev1 Spl@222')
# os.system('xcopy X: Y: /E /I /H /K /Y')
# os.system('net use X: /delete')
# os.system('net use Y: /delete')

backupDone = False
while True:
	connection = mysql.connector.connect(
		host=dbData['host'],
		user=dbData['user'],
		password=dbData['password'],
		database=dbData['database']
	) 
	# Create a cursor object to execute SQL queries
	cursor = connection.cursor()
	
	# Define the SQL query to drop the table if it exists
	query = "SELECT * FROM scripts WHERE id="+scriptID
	cursor.execute(query)
	script = cursor.fetchone()
	running_status = script[4]

	backup_time_1 = script[6]
	backup_time_2 = script[7]
	backup_time_3 = script[8]
	backup_time_4 = script[9]

	# Execute the SQL query
	cursor.execute(query)
	script = cursor.fetchone()

	src = script[1]
	dst = script[2]

	query = "SELECT * FROM paths WHERE id="+str(src)
	cursor.execute(query)
	source = cursor.fetchone()
	src_server = source[1]
	src_path = source[2]
	src_user = source[3]
	src_pass = decrypt12(source[4])
	src_alias = source[5]

	query = "SELECT * FROM paths WHERE id="+str(dst)
	cursor.execute(query)
	destination = cursor.fetchone()

	dst_server = destination[1]
	dst_path = destination[2]
	dst_user = destination[3]
	dst_pass = decrypt12(destination[4])
	dst_alias = destination[5]
	

	if(running_status == 1):
		t = current_datetime.strftime("%H:%M")
		if((t == backup_time_1 or t == backup_time_2 or t == backup_time_3 or t == backup_time_4) and not backupDone):
			copy_all('\\\\'+src_server+'\\'+src_path,'\\\\'+dst_server+'\\'+dst_path)
			print(t)
			print('Backup Done')
			
			backupDone = True


	elif(running_status == 0):
		sys.exit()

	cursor.close()
	connection.close()
	current_datetime = datetime.now()
	time.sleep(5)
	
	if((t != backup_time_1 and t != backup_time_2 and t != backup_time_3 and t != backup_time_4) and backupDone):
		backupDone = False
	# formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
	# formatted_datetime = current_datetime.strftime("%H:%M")
	
	











# what is the OS in server ?
# Should number of script one ?
# Should backup directory name change everyday ?