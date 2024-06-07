#TEST MAPPED DIRECTORY

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

serverID = arguments[1]


def decrypt12(text):
	d = ""
	for ch in text:
		d += chr(ord(ch)+12)
	return d

# Open the JSON file
with open('db-config.json', 'r') as file:
	# Load JSON data
	dbData = json.load(file)

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
query = "SELECT * FROM servers WHERE id="+serverID

cursor.execute(query)

server = cursor.fetchone()

if(server):
	server_address = server[2]
	server_username = server[3]
	server_password = decrypt12(server[4])

	try:
		register_session(server_address, username=server_username, password=server_password)	
		print("Connected")
	except:
		print("Failed")
else:
	print("ServerNotFoundError")