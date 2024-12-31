import json
import google.generativeai as genai
import os

class AnalizadorDeReseñas:
    def __init__(self):
        genai.configure(api_key=os.getenv('api_key'))
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Inicializar el modelo
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=self.generation_config
        )
        
        # Definir el prompt del sistema
        self.system_prompt = """
        Eres un asistente de pizzería que responde de manera fluida y natural.
        Debes responder siempre en formato JSON usando esta estructura exacta, las opciones para botones no deben ser muy largas, el titulo debe ser de 24 caracteres: {"respuesta": "tu respuesta aquí"}
        """

    def generar_info(self, data):
        chat = self.model.start_chat(history=[])
        prompt = f"{self.system_prompt}\nPregunta del cliente: {data}"
        response = chat.send_message(prompt)
        return response.text

    def obtener_info(self, data):
        try:
            respuesta = self.generar_info(data)
            return json.loads(respuesta)["respuesta"]
        except json.JSONDecodeError:
            return "Lo siento, hubo un error al procesar la respuesta."

