

import json
from tdameritrade.auth import authentication
from tdameritrade import TDClient
import datetime
from config import USERNAME, PASSWORD, RETURN_URL, APP_TOKEN

def access_client(token):
	return TDClient(token["access_token"]) if "access_token" in token else None

def main():
	token = {}
	try:
		# Attempts to open the existing Token file if it exists.
		with open("token.json", "r") as fp:
			token = json.load(fp)
		if "last_authenticated" not in token:
			print("No last Authentication Datetime")
			raise ValueError
		if "expires_in" not in token:
			print("No Known Expiration")
			raise ValueError
		d = datetime.datetime.fromisoformat(token["last_authenticated"])
		expiration = d + datetime.timedelta(0, token["expires_in"])
		if expiration < datetime.datetime.now():
			print("Token Expired")
			raise ValueError
	except:
		#If it doesnt exist, follow authentication protocol
		token = authentication(APP_TOKEN, RETURN_URL, USERNAME, PASSWORD)
		with open("token.json", "w") as fp:
			token["last_authenticated"] = datetime.datetime.now().isoformat()
			json.dump(token, fp)
	print("Token info:", token)
	client = access_client(token)
	if client is None:
		return
	print("Test attempt to See Client Accounts:")
	accounts = client.accounts()
	print("Accounts", accounts)

if __name__ == "__main__":
	main()