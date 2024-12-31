import json
import requests
import time


whatsapp_token = 'EAAE94ZB5JKZBEBOzeLZBr1CP5EG4IUXjjkyOpsvRjGQgEJijFb8xRTDDs4ZA0QM3ba0MkZAZA6U8LHr1lvcgTiVHY4FW2BZA4ufQbiFU7CNFb8sULgQgflgG9fQ8ZCTMQavgAJQlkZAu1zkNYcEJkPhNKw1HfLzdaAZCbskARGQtaCpFdUaEUhtZAcvUvmnbuCNSiaiYYtv4jRLn1uDXcuBL6k0VxcQqdQZD'
whatsapp_url = 'https://graph.facebook.com/v21.0/376680255522592/messages'

# Función para enviar mensajes de texto manualmente
def enviar_mensaje_manualmente(numero, mensaje):
    try:
        data = json.dumps({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "body": mensaje
            }
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + whatsapp_token
        }
        
        response = requests.post(whatsapp_url, headers=headers, data=data)
        
        if response.status_code == 200:
            print(f'Mensaje enviado a {numero} correctamente.')
        else:
            print(f'Error al enviar mensaje a {numero}. Código de estado: {response.status_code}')
    except Exception as e:
        print(f'Error al enviar mensaje a {numero}: {e}')

# Función para capturar el número y el mensaje desde la consola y luego enviarlo
def capturar_y_enviar_mensaje():
    try:
        numero = input("Ingrese el número de teléfono (sin espacios ni guiones): ")
        mensaje = input("Ingrese el mensaje que desea enviar: ")

        enviar_mensaje_manualmente(numero, mensaje)
    except Exception as e:
        print(f'Error al capturar y enviar mensaje: {e}')

# Ejemplo de cómo usar la función
capturar_y_enviar_mensaje()  # Puedes descomentar esta línea para probarlo manualmente
