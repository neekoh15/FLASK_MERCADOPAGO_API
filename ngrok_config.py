# import ngrok python sdk
import ngrok
import time, json
import threading


class NGROK_FORWARD:
    def __init__(self, ) -> None:

        with open('config.json', 'r+') as config_file:
            file = json.load(config_file)
            self.PORT = file.get("PORT")
            NGROK_AUTH_TOKEN = file.get("NGROK_AUTH_TOKEN")

            self.static_domain = file.get("NGROK_STATIC_DOMAIN")

        ngrok.set_auth_token(NGROK_AUTH_TOKEN)

    def start_listener(self):

        self.listener = ngrok.forward(self.PORT)

        # Output ngrok url to console
        print(f"Ingress established at {self.listener.url()}")


    def start(self):
        # Crear un hilo para el listener
        listener_thread = threading.Thread(target=self.start_listener)
        listener_thread.daemon = True  # Permite que el hilo se cierre al finalizar el programa principal
        listener_thread.start()