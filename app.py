from flask import Flask, request, render_template   
import sett 
import services
from flask import jsonify
import os


app = Flask(__name__)

@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    return 'Hola, desde Flask'

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = services.replace_start(message['from'])
        messageId = message['id']
        # contacts = value['contacts'][0]
        # name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)
        

        response = services.administrar_chatbot(text, number, messageId, "Usuario Web")
        return jsonify({"status": "success", "response": response})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

