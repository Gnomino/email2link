from flask import Flask, request
import json, requests, random, os
app = Flask(__name__)
with open('config.json', 'r') as f:
	config = json.loads(f.read())
def generate_name(length=5):
	chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
	return ''.join( random.choice(chars) for i in range(length))
def allowed_file(name):
    if '.' not in name:
    	return False
    ext = name.rsplit('.', 1)[1].lower()
    if ext in ["jpg", "png", "gif", "jpeg"]:
    	return ext
    else:
    	return False
@app.route(config['route'], methods=["POST"])
def index():
	urls = []
	filenames = []
	for attachment in request.files.values():
		ext = allowed_file(attachment.filename)
		if ext:
			newFilename = generate_name() + "." + ext
			attachment.save(config['images_folder'] + newFilename)
			urls.append(config['hosting_domain'] + newFilename)
			filenames.append(attachment.filename)
	if not urls:
		return 'ERROR'
	maildata = {"from": config['from_email'], "to": request.form["from"], "subject": ", ".join(filenames)}
	messageHTML = "Your images were successfully uploaded : <br>"
	messageTXT = "Your images were successfully uploaded : \r\n"
	for i in range(len(filenames)):
		messageHTML += filenames[i] + " : <a href=\"" + urls[i] + "\">" + urls[i] + "</a><br>"
		messageTXT += filenames[i] + " : " + urls[i] + "\r\n"
	maildata['html'] = messageHTML
	maildata['text'] = messageTXT
	r = requests.post("https://api.mailgun.net/v3/" + config['mailgun_domain'] + "/messages", auth=("api", config["mailgun_api"]), data=maildata)
	return 'OK'
	
if __name__ == '__main__':
	app.run(host=config['ip'], port=config['port'])
