import random
import datetime
from cassandra.cluster import Cluster
from cassandra.util import uuid_from_time

print("Conectando a ScyllaDB para inyección masiva...")
cassandra_cluster = Cluster(['127.0.0.1'])
scylla_session = cassandra_cluster.connect('discord_mock')

# Inyección Asincrónica: 
# Al no bloquear el hilo esperando la confirmación del disco, 
# logramos el insert masivo, simulando el tráfico real de un chat como Discord.

canales = [10, 20]
usuarios = [1, 2, 3, 4, 5]
textos_base = [
    "¿Pudieron levantar el docker-compose?",
    "Fíjate si el puerto 9042 está abierto en el firewall, capaz es eso.",
    "Revisen las reglas de iptables, por ahí viene el bloqueo de red.",
    "¿Usamos RAID 5 para el servidor de storage o es mucho para este TP?",
    "No me hace ping la máquina virtual del Gateway.",
    "Gente, armé un checklist de OPSEC nivel 1 para aplicar al proyecto.",
    "El servidor tiene 8GB de RAM, con Debian 13 debería volar.",
    "Revisen la documentación de la API, creo que cambió el endpoint.",
    "El rollback está funcionando perfecto.",
    "Acabo de pushear a main, crucen los dedos 💀",
    "Me tiró un warning gigante pero compila jajaja.",
    "**Solucionado**, era un problema de permisos en los roles.",
    "¿A qué hora es la reunión de la tesis?",
    "Acuérdense de comentar el código para la defensa de Bases de Datos.",
    "El profesor nos va a matar con las consultas de arquitectura.",
    "Jajaja, me pasó lo mismo ayer.",
    "Cayó el campus virtual de la facultad otra vez...",
    "¿Quién se prende a jugar algo a la noche para relajar?",
    "Excelente avance equipo. ¡Ya casi lo tenemos!",
    "No doy más de sueño, mañana sigo con el DER.",
    "Sale esa juntada por acá para repasar para el final.",
    '{"tipo": "archivo", "nombre": "log_servidor.txt", "size": "15kb"}',
    '{"tipo": "imagen", "url": "https://discord.mock/img/der_final.png", "width": 1920}',
    '{"tipo": "audio", "duracion": "0:45", "transcript": "null"}'
]

mensajes_a_generar = 500
fecha_inicio = datetime.datetime(2026, 5, 1) # Desde el 1 de mayo de 2026
fecha_fin = datetime.datetime(2026, 7, 1)    # Hasta el 1 de julio de 2026

print(f"Generando {mensajes_a_generar} mensajes históricos...")

for _ in range(mensajes_a_generar):
    # 1. Datos aleatorios
    canal = random.choice(canales)
    autor = random.choice(usuarios)
    contenido = random.choice(textos_base)
    
    # 2. Generar una fecha aleatoria entre inicio y fin
    tiempo_random = fecha_inicio + datetime.timedelta(
        seconds=random.randint(0, int((fecha_fin - fecha_inicio).total_seconds()))
    )
    
    # 3. Truncar el bucket al día 1 de ese mes aleatorio
    bucket = tiempo_random.replace(day=1).date()
    
    # 4. Generar el TIMEUUID con la fecha exacta aleatoria
    falso_uuid = uuid_from_time(tiempo_random)
    
    # 5. Insertar en ScyllaDB
    scylla_session.execute(
        """
        INSERT INTO messages (channel_id, bucket, message_id, author_id, content)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (canal, bucket, falso_uuid, autor, contenido)
    )

cassandra_cluster.shutdown()
print("¡Inyección masiva completada con éxito!")