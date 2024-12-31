import requests
import os
import json
import time
from Reseña_Analisis import AnalizadorDeReseñas
from datetime import datetime
import sqlite3
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import ssl

# Configuración de MongoDB con opciones SSL específicas
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://guerrasebastian16:<db_password>@chatbot.gixrn.mongodb.net/?retryWrites=true&w=majority&appName=ChatBot')

# Configuración del cliente con opciones SSL específicas
client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi('1'),
    tlsCAFile=certifi.where(),
    ssl=True,
    ssl_cert_reqs=ssl.CERT_NONE,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    serverSelectionTimeoutMS=30000
)

try:
    db = client['whatsapp_bot']
    messages_collection = db['messages']
except Exception as e:
    print(f"Error inicial al conectar con MongoDB en services: {e}")
    db = None
    messages_collection = None

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = os.environ.get('WHATSAPP_TOKEN')  # Asegúrate de que sea el nombre correcto
        whatsapp_url = os.environ.get('WHATSAPP_URL')
        
        if not whatsapp_token or not whatsapp_url:
            print("Error: Token o URL no configurados")
            return 'Error de configuración', 500

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {whatsapp_token}'
        }
        
        
        response = requests.post(whatsapp_url, headers=headers, data=data)

        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return response.text
        else:
            error_msg = f'Error al enviar mensaje: {response.status_code} - {response.text}'
            print(error_msg)
            return (error_msg, response.status_code)
         
            
    except Exception as e:
        print("Error en enviar_Mensaje_whatsapp:", str(e))
        return str(e), 403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        # Limitar el título a 24 caracteres
        title = option[:24] if len(option) > 24 else option
        description = option[24:] if len(option) > 24 else ""
        
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": title,
                "description": description
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = os.getenv('stickers').get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data



def save_message(number, text, responses, messageId):
    try:
        # Guardar el mensaje del usuario
        user_message = {
            "phone_number": number,
            "message_text": text,
            "response": None,
            "timestamp": datetime.now(),
            "message_id": messageId,
            "is_user": True
        }
        messages_collection.insert_one(user_message)
        
        # Extraer y guardar las respuestas del bot
        for response in responses:
            try:
                response_data = json.loads(response[0])
                bot_message = ""
                
                # Extraer el texto según el tipo de mensaje
                if response_data.get('type') == 'text':
                    bot_message = response_data['text']['body']
                elif response_data.get('type') == 'reaction':
                    continue
                elif response_data.get('type') == 'interactive':
                    if 'interactive' in response_data:
                        if 'body' in response_data['interactive']:
                            bot_message = response_data['interactive']['body']['text']
                            
                        # Agregar opciones al mensaje
                        if 'action' in response_data['interactive']:
                            if 'buttons' in response_data['interactive']['action']:
                                options = [btn['reply']['title'] for btn in response_data['interactive']['action']['buttons']]
                                bot_message += "\nOpciones: " + ", ".join(options)
                            elif 'sections' in response_data['interactive']['action']:
                                options = [row['title'] for section in response_data['interactive']['action']['sections'] for row in section['rows']]
                                bot_message += "\nOpciones: " + ", ".join(options)
                
                if bot_message:
                    response_status = "sent" if isinstance(response[1], str) else str(response[1])
                    bot_response = {
                        "phone_number": number,
                        "message_text": bot_message,
                        "response": response_status,
                        "timestamp": datetime.now(),
                        "message_id": None,
                        "is_user": False
                    }
                    messages_collection.insert_one(bot_response)
                
            except Exception as e:
                print(f"Error procesando respuesta: {e}")
                continue
            
        print("Mensaje guardado correctamente")
    except Exception as e:
        print(f"Error guardando mensaje: {e}")


def administrar_chatbot(text,number, messageId, name):
    text = text.lower()
    list = []
    print("mensaje de "+ name + ": ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    if any(greeting in text for greeting in ["hola", "buenos dias", "buenas tardes", "buenas noches", "hey"]):
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "Equipo La Pizzada"
        options = ["🍕 Ver Menú", "🛵 Hacer Pedido", "❓ Información"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "👋")
        list.append(replyReaction)
        list.append(replyButtonData)

    elif any(menu in text for menu in ["ver menú", "menu", "carta", "que tienen"]):
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada - Menú"
        options = ["🍕 Pizzas", "🥤 Bebidas", "🍨 Postres"]

        listReplyData = listReply_Message(number, options, body, footer, "sed2",messageId)
        list.append(listReplyData)

    elif "pizzas" in text:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "Todas las pizzas incluyen queso mozzarella"
        options = ["Margherita $15.000", "Pepperoni $18.000", "Hawaiana $17.000", "Vegetariana $16.000"]

        listReplyData = listReply_Message(number, options, body, footer, "sed3",messageId)
        list.append(listReplyData)

    elif "hacer pedido" in text:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada"
        options = ["📱 WhatsApp", "📞 Llamada", "🏠 Delivery"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4",messageId)
        list.append(replyButtonData)

    elif "información" in text:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada"
        options = ["🕒 Horarios", "📍 Ubicación", "💳 Métodos de pago"]

        listReplyData = listReply_Message(number, options, body, footer, "sed5",messageId)
        list.append(listReplyData)

    elif "horarios" in text:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada"
        options = ["🕒 Nuestros horarios son:\nLunes a Jueves: 12:00 - 22:00\nViernes y Sábado: 12:00 - 00:00\nDomingo: 12:00 - 21:00"]

        listReplyData = listReply_Message(number, options, body, footer, "sed6",messageId)
        list.append(listReplyData)

    elif "ubicación" in text:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada"
        options = ["📍 Nos encontramos en:\nCalle Principal #123\nBarrio Centro\n\n¡Te esperamos!"]

        listReplyData = listReply_Message(number, options, body, footer, "sed7",messageId)
        list.append(listReplyData)

    elif "métodos de pago" in text:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada"
        options = ["💳 Aceptamos:\n- Efectivo\n- Tarjetas de crédito/débito\n- Transferencias bancarias\n- PSE"]

        listReplyData = listReply_Message(number, options, body, footer, "sed8",messageId)
        list.append(listReplyData)

    elif "gracias" in text:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada"
        options = ["¡Gracias a ti! 🙏 Esperamos verte pronto en La Pizzada. ¡Que tengas un excelente día! 😊"]

        listReplyData = listReply_Message(number, options, body, footer, "sed9",messageId)
        list.append(listReplyData)

    else:
        analizador = AnalizadorDeReseñas()
        respuesta = analizador.obtener_info(text)
        # print("IA Response", respuesta)    
        body = respuesta
        footer = "La Pizzada"
        options = ["Lo siento, no entendí tu mensaje. Puedes escribir 'hola' para ver el menú principal o 'información' para más detalles sobre nuestro servicio. 😊"]

        listReplyData = listReply_Message(number, options, body, footer, "sed10",messageId)
        list.append(listReplyData)

    responses = []
    for item in list:
        response = enviar_Mensaje_whatsapp(item)
        responses.append((item, response[0]))  # Guardamos el mensaje enviado y su respuesta
    
    # Guardar mensajes en la BD
    save_message(number, text, responses, messageId)
    
    return [resp[1] for resp in responses]

#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s

# para argentina
def replace_start(s):
    if s.startswith("549"):
        return "54" + s[3:]
    else:
        return s
