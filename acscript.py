from smbclient import link, open_file, register_session, remove, rename, stat, symlink, listdir
from smbprotocol.session import Session
import os
import sys
import time
import json
import mysql.connector
from datetime import datetime


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

def in_history(filename):
	sql = f"SELECT * FROM script_{scriptID} WHERE filename = '{filename}'"

	cursor.execute(sql)
	data = cursor.fetchone()
	
	if(data):
		return True
	return False	

def push_in_history(filename):
	# Get the current date and time
	current_datetime = datetime.now()
	formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

	sql = f"INSERT INTO script_{scriptID}(filename,created_at) VALUES('{filename}','{formatted_datetime}')"
	# print(sql)
	cursor.execute(sql)
	connection.commit()
	# cursor.commit()
	
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
	

def list_and_copy_files(server_address, share_name, username, password,dst_server,dst_dir,dst_username,dst_password):
	try:
		register_session(server_address, username=username, password=password)	
	except:	
		log_error(f"ScriptID:{scriptID}","Unable To register session in source")
		log_error(f"ScriptID:{scriptID}","Script has been stopped")	
		stop_script()
		sys.exit()
	smb_path = f"\\\\{server_address}\\{share_name}"
	files = listdir(smb_path)
	for file in files:
		try:
			with open_file(f"{smb_path}\\{file}",mode="r",encoding="utf-8") as srcFile:
				fileContents = srcFile.read()
				file_name=os.path.basename(file)
				if(in_history(file_name)):
					print("in")
					continue
				charactersSize = len(fileContents)
				time.sleep(1)
				if(charactersSize < len(fileContents)):
					time.sleep(10)

				try:
					try:
						register_session(dst_server, username=dst_username, password=dst_password)
					except:
						log_error(f"ScriptID:{scriptID}","Unable To register session in destination")
						log_error(f"ScriptID:{scriptID}","Script has been stopped")	
						stop_script()
						sys.exit()
					smb_path2 = f"\\\\{dst_server}\\{dst_dir}"
					with open_file(f"{smb_path2}\\{file}",mode="w",encoding="utf-8") as dstFile:
						dstFile.write(fileContents)
					push_in_history(file_name)
				except:
					log_error(f"ScriptID:{scriptID}","Error: Path Error {dst_server}")
					log_error(f"ScriptID:{scriptID}","Script has been stopped")
					stop_script()

		
		except UnicodeDecodeError:
			with open_file(f"{smb_path}\\{file}",mode="rb",encoding="utf-8") as srcFile:
				fileContents = srcFile.read()
				file_name=os.path.basename(file)
				if(in_history(file_name)):
					print("in")
					continue
				charactersSize = len(fileContents)
				time.sleep(1)
				if(charactersSize < len(fileContents)):
					time.sleep(10)

				try:
					try:
						register_session(dst_server, username=dst_username, password=dst_password)
					except:
						log_error(f"ScriptID:{scriptID}","Unable To register session in destination")
						log_error(f"ScriptID:{scriptID}","Script has been stopped")	
						stop_script()
						sys.exit()
					smb_path2 = f"\\\\{dst_server}\\{dst_dir}"
					with open_file(f"{smb_path2}\\{file}",mode="wb",encoding="utf-8") as dstFile:
						dstFile.write(fileContents)
					push_in_history(file_name)
				except:
					log_error(f"ScriptID:{scriptID}","Error: Path Error {dst_server}")
					log_error(f"ScriptID:{scriptID}","Script has been stopped")
					stop_script()				
		except:
			file_name=os.path.basename(file)
			log_error(f"ScriptID:{scriptID}",f"Filename {file_name} Error:UnknownError {str(smb_path)}")
			log_error(f"ScriptID:{scriptID}","Script has been stopped")
			stop_script()
			
# Open the JSON file
with open('db-config.json', 'r') as file:
	# Load JSON data
	dbData = json.load(file)

pid = os.getpid()   





# print(dbData);
# list_and_copy_files('192.168.5.235', 'share\\src', 'DEV02', 'Spl@222','192.168.5.235', 'share\\dst', 'DEV02', 'Spl@222')  


while True:
	# Connect Database
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

	query = "SELECT * FROM paths WHERE id="+str(dst)
	cursor.execute(query)
	destination = cursor.fetchone()

	dst_server = destination[1]
	dst_path = destination[2]
	dst_user = destination[3]
	dst_pass = decrypt12(destination[4])

	

	running_status = script[4]
	if(running_status == 1):
		list_and_copy_files(src_server, src_path, src_user, src_pass,dst_server, dst_path, dst_user, dst_pass)
		# print(script)
		print(script[3])
		print("Process ID:", pid)
		print("Script ID:",scriptID)
	elif(running_status == 0):
		sys.exit()	

	cursor.close()
	connection.close()
	time.sleep(5)
