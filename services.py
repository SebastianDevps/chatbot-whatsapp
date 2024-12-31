import requests
import sett
import json
import time
from flask import request, jsonify
from Reseña_Analisis import AnalizadorDeReseñas

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
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
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
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
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
        media_id = sett.stickers.get(media_name, None)
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



def administrar_chatbot(text,number, messageId, name):
    text = text.lower()
    list = []
    print("mensaje del usuario: ",text)

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
        responses.append(response)

    return responses

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
