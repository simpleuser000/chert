import telebot
from telebot import util
import requests as rq
import json
from time import sleep
import multiprocessing as mp
import random

auth_key = 'Bearer lD58T2N2MhrOGTEDD9g-1YklZ9TBufUS1wO2mo0c'
email = 'Heshmatali73@outlook.com'

hercoll_zone_id = 'ded39e06829e160d61be64d36b22a214'
divar_zone_id = '52572735345003ba3dd1a1a818cf8bd2'

hercoll_url = f'https://api.cloudflare.com/client/v4/zones/{hercoll_zone_id}/dns_records'
divar_url = f'https://api.cloudflare.com/client/v4/zones/{divar_zone_id}/dns_records' 
urls = [divar_url , hercoll_url]
headers = {
    'Content-Type': 'application/json',
    'Authorization': auth_key
}

useless_records = ["meta", "tags", "id", "zone_id",
                   "proxiable", "ttl", "locked", "created_on",
                   "modified_on"]

API_TOKEN = "6029245172:AAEd8tEe8wRAptZW1VWwJXxyBY1NcDcQzsg"
bot = telebot.TeleBot(API_TOKEN)


def edit_dns_records(chose_zone, record_num, list_changes):
	if chose_zone == "hercoll.online":
		request = rq.get(hercoll_url, headers=headers).json()
		url = hercoll_url
	elif chose_zone == "divar.tech":
		request   = rq.get(divar_url  , headers=headers).json()
		url = divar_url

	record_content = request["result"][int(record_num)]
	record_id      = record_content["id"]
	url            = f"{url}/{record_id}"
	
	if list_changes[0] != "none":
		record_content["name"] = list_changes[0]
	if list_changes[1] != "none":
		record_content["content"] = list_changes[1]
	if list_changes[2] != "none":
		record_content["type"] = list_changes[2]
	
	update_zone_record = rq.patch(url, headers=headers, json=record_content)
	if update_zone_record.status_code == 200:
		return True
	else:
		return False

def load_balancer(live_time, ip_list, record_num_hercoll, record_num_divar):
	hercoll_request = rq.get(hercoll_url, headers=headers).json()
	divar_request   = rq.get(divar_url  , headers=headers).json()

	hercoll_record_content = hercoll_request["result"][int(record_num_hercoll)]
	divar_record_content   = divar_request["result"][int(record_num_divar)]

	hercoll_record_id = hercoll_record_content["id"]
	divar_record_id   = divar_record_content["id"]

	hercoll_record_url = f"{hercoll_url}/{hercoll_record_id}"
	divar_record_url   = f"{divar_url}/{divar_record_id}"

	# if length of ip is not more than 2 we will not use random
	# lib to change ip , becuse There is no randomness here and 
	# the ip states do not exceed 2.
	if len(ip_list) == 2:
		while True:
			hercoll_current_ip = ip_list[0]
			divar_current_ip   = ip_list[1]

			hercoll_record_content["content"] = hercoll_current_ip
			divar_record_content["content"]   = divar_current_ip

			hercoll_record_update = rq.patch(hercoll_record_url, headers=headers, json=hercoll_record_content)

			divar_record_update = rq.patch(divar_record_url  , headers=headers, json=divar_record_content)

			sleep(live_time)
			print("-"*20)
			divar_current_ip   = ip_list[0]
			hercoll_current_ip = ip_list[1]

			hercoll_record_content["content"] = hercoll_current_ip
			divar_record_content["content"]   = divar_current_ip

			hercoll_record_update = rq.patch(hercoll_record_url, headers=headers, json=hercoll_record_content)

			divar_record_update = rq.patch(divar_record_url  , headers=headers, json=divar_record_content)
			
			sleep(live_time)

	first_loop = True
	while True:
		if first_loop == True:
			hercoll_current_ip = ip_list.pop ( ip_list.index( random.choice( ip_list ) ) )
			divar_current_ip   = ip_list.pop ( ip_list.index( random.choice( ip_list ) ) )

			ip_list.insert(0, hercoll_current_ip)
			ip_list.insert(0, divar_current_ip)

			hercoll_record_content["content"] = hercoll_current_ip
			divar_record_content["content"]   = divar_current_ip

			hercoll_record_update = rq.patch(hercoll_record_url, headers=headers, json=hercoll_record_content)
			divar_record_update = rq.patch(divar_record_url  , headers=headers, json=divar_record_content)

			first_loop = False

		else:

			hercoll_current_ip = ip_list.pop ( ip_list.index( random.choice( ip_list[2:] ) ) )
			divar_current_ip   = ip_list.pop ( ip_list.index( random.choice( ip_list[2:] ) ) )

			ip_list.insert(0, hercoll_current_ip)
			ip_list.insert(0, divar_current_ip)

			hercoll_record_content["content"] = hercoll_current_ip
			divar_record_content["content"]   = divar_current_ip

			hercoll_record_update = rq.patch(hercoll_record_url, headers=headers, json=hercoll_record_content)
			divar_record_update = rq.patch(divar_record_url  , headers=headers, json=divar_record_content)

		sleep(live_time)

# start running bot
@bot.message_handler(commands=["list"])
def list_dns_record(message):
    list_help = "Usage: /list [zone_name]"
    args = message.text.split()[1:]
    urls = [hercoll_url, divar_url]
    if len(args) > 0:
        url = args[0]
        list_records = str()
        for i in urls:
           records = rq.get(i, headers=headers).json()
           zones = records['result'][0]['zone_name']
           if url in zones:
                zone_selected = records['result'][0]['zone_id']
                zone_url = f"https://api.cloudflare.com/client/v4/zones/{zone_selected}/dns_records" 
                zone_data = rq.get(zone_url, headers=headers).json()
                # zone_data_result = zone_data["result"][0]
                for j in range(len(zone_data['result'])):
                    list_records += f"[{j}]\n"
                    for key in zone_data['result'][j]:
                        if key in useless_records:
                            continue
                        value = zone_data["result"][j][key]
                        list_records += f"{key} : {value}\n"
                    list_records += (str("-"*30) + "\n")
                list_records += ("record count :" + str(len(zone_data["result"])))
                bot.send_message(message.chat.id, list_records) 
                return
        else:
            bot.send_message(message.chat.id, "Zone Not Found !")
    else:
        bot.send_message(message.chat.id, list_help)

# start create dns record
@bot.message_handler(commands=["create"])
def create_dns_record(message):
	args = message.text.split()[1:]
	if len(args) == 4:
		data = {
			"name":args[1],
			"content": args[2],
			"type": args[3]
		}
		if args[0] == "hercoll.online":
			request = rq.get(hercoll_url, headers=headers).json()
			url = hercoll_url
		elif args[0] == "divar.tech":
			request = rq.get(divar_url, headers=headers).json()
			url = divar_url

		#record_content = request["result"][int(args[4])]

		stat = rq.post(url, headers=headers, json=data)
		if stat.status_code == 200:
			bot.send_message(message.chat.id, "record created")
		else:
			bot.send_message(message.chat.id, "problem in create record")	


	else:
		bot.send_message(message.chat.id, "Usage: /create [domain] [name] [ip] [type]")
		bot.send_message(message.chat.id, "example: /create divar.tech hello 3.3.3.3 A") 



@bot.message_handler(commands=["remove"])
def remove_dns_record(message):
    args = message.text.split()[1:]
    if (len(args)) > 0:
        url = args[0]
        record_name = args[1]
        ip_address = args[2]
        for i in urls:
           records = rq.get(i, headers=headers).json()
           if records['result']:
               zones = records['result'][0]['zone_name'] 
               if url in zones:
                    zone_selected = records['result'][0]['zone_id']
                    zone_url = f"https://api.cloudflare.com/client/v4/zones/{zone_selected}/dns_records" 
                    zone_data = rq.get(zone_url, headers=headers).json()
                    if record_name == zone_data["result"][0]["name"] and ip_address == zone_data["result"][0]["content"]:
                        record_id = zone_data["result"][0]["id"]
                        zone_id = zone_data["result"][0]["zone_id"]
                        
                        delete = rq.delete(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}", headers=headers)
                        if delete.json()["success"]:
                            bot.send_message(message.chat.id, "Delete Record Success") 
                        else:
                            bot.send_message(message.chat.id, "Delete Record Faild !")  
                    else:
                        bot.send_message(message.chat.id, "Record Name or IP Address Wrong") 
                    return
    else:
        bot.send_message(message.chat.id, "Usage: /Remove Zone_Name , RecordName , ip Address")
	
	 
# start edit dns record
@bot.message_handler(commands=["edit"])
def edit_dns_record(message):
	args = message.text.split()[1:]
	urls = [hercoll_url, divar_url]
	if len(args) == 5:
		changes = [args[2], args[3], args[4]]
		stat = edit_dns_records(args[0], args[1], changes)
		if stat == True:
			bot.send_message(message.chat.id, "record edited")
		else:
			bot.send_message(message.chat.id, "problem in edit record")
	else:
		bot.send_message(message.chat.id, "Usage: /edit [domain_name] [record_number] [name] [ip] [type]")
		bot.send_message(message.chat.id, "example: /edit [divar.tech] [3] [test1] [1.1.1.1] [A]")

# start load balancer 
@bot.message_handler(commands=["load"])
def load_balancer_domain(message):
	global run_lb
	args = message.text.split()[1:]
	if len(args) == 4:
		ip_list = args[1].split(",")
		print(ip_list)
		run_lb = mp.Process(target=load_balancer, args=(args[0], ip_list, args[2], args[3]))
		run_lb.start()
	elif len(args) == 1 and args[0] == "stop":
		if run_lb.is_alive():
			run_lb.terminate()
			bot.send_message(message.chat.id, "load balancer stopped")
		else:
			bot.send_message(message.chat.id, "load balancer is not running")
	else:
		bot.send_message(message.chat.id, "for running load balancer: ")
		bot.send_message(message.chat.id, "Usage: /load [time] [list ip] [record number hercoll] [record number divar]")
		bot.send_message(message.chat.id, "example: /load 10 1.1.1.1,2.2.2.2,3.3.3.3 1 2")
		bot.send_message(message.chat.id, "for stopping load balancer: ")
		bot.send_message(message.chat.id, "Usage: /load stop")

bot.infinity_polling()