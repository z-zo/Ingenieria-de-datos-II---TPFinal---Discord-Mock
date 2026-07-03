import psycopg2
from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
import datetime
import time

class DiscordDataService:
    def __init__(self):
        # Inicia el docker de Postgres (pg es la nomenclatura estandar)
        print("Conectando a PostgreSQL...")
        self.pg_conn = psycopg2.connect(
            dbname="discord_db", 
            user="postgres", 
            password="password", 
            host="127.0.0.1",
            port="5432"
        )
        self.pg_conn.autocommit = False # CRÍTICO: Mantenemos el control para el Rollback
        
        # Inicio del docker de Scylla (discord_mock ya fue creado antes por terminal)
        print("Conectando a ScyllaDB...")
        self.cassandra_cluster = Cluster(['127.0.0.1'])
        self.scylla_session = self.cassandra_cluster.connect('discord_mock')
        print("Infraestructura conectada con éxito.\n")

    def enviarMensaje(self, user_id, server_id, channel_id, content):
        cursor = self.pg_conn.cursor()
        
        try:
            # prints para visualizar paso a paso
            print(f"--- Iniciando transacción para el usuario {user_id} en canal {channel_id} ---")
            
            # Primero que existan lo permisos (ser miembro del servidor, miembro del canal y tenga el permiso de mandar mensajes)
            cursor.execute(
                "SELECT 1 FROM ServerMembers WHERE user_id = %s AND server_id = %s",
                (user_id, server_id)
            )
            # Si no encuentra coincidencia:
            if not cursor.fetchone():
                raise PermissionError("Validación fallida: El usuario no pertenece a este servidor.")

            # Segundo comienza la transaccion (aun local)
            # Incrementamos el contador, si falla el paso siguiente, revertiremos esto en el ROLLBACK
            cursor.execute(
                "UPDATE ServerMembers SET message_count = message_count + 1 WHERE user_id = %s AND server_id = %s", 
                (user_id, server_id)
            )
            
            cursor.execute(
                "UPDATE Channels SET last_activity_at = CURRENT_TIMESTAMP WHERE channel_id = %s", 
                (channel_id,)
            )

            # Tercero, de damos formato a la fecha (la truncamos)
            # Un problema que encontramos es que el bucket, que deberia particionar por mes, es un texto manual, pero si lo pasamos a DATE
            # la particion seria por dia, ver la historia de una semana serian 7 tokens distinto. Nuestra solucion, truncar el datetime desde
            # el orquestrador
            fecha_actual = datetime.datetime.now()
            bucket_optimizado = fecha_actual.replace(day=1).date()
            
            # Preparamos la consulta exigiendo QUORUM (Consistencia fuerte)
            query = SimpleStatement(
                """
                INSERT INTO messages (channel_id, bucket, message_id, author_id, content)
                VALUES (%s, %s, now(), %s, %s)
                """,
                consistency_level=ConsistencyLevel.QUORUM
            )
            
            # intentamos la escritura en el motor NoSQL
            self.scylla_session.execute(query, (channel_id, bucket_optimizado, user_id, content))

            # Si nada fallo hasta acá, exito y commiteamos
            self.pg_conn.commit()
            # print the confirmacion
            print("ÉXITO: Mensaje guardado y contadores actualizados de forma sincronizada.")
        
        # si algun paso falla, ROLLBACK
        except PermissionError as pe:
            self.pg_conn.rollback()
            print(f"ERROR IRRECUPERABLE (Seguridad): {pe}")
            
        except Exception as e:
            # Rollback Manual
            self.pg_conn.rollback()
            print(f"ERROR DE INFRAESTRUCTURA (ScyllaDB falló). Ejecutando ROLLBACK en Postgres.")
            print(f"Detalle del error: {e}")
            
        finally:
            cursor.close()

    def cerrar_conexiones(self):
        self.pg_conn.close()
        self.cassandra_cluster.shutdown()

# PRUEBA
if __name__ == "__main__":
    servicio = DiscordDataService()
    
    # Prueba 1: Transacción exitosa (Usuario 1 en Servidor 100 y Canal 1001)
    servicio.enviarMensaje(
        user_id=1, 
        server_id=100, 
        channel_id=1001, 
        content="Mensaje procesado a través del orquestador Python."
    )
    
    # Prueba 2: Fallo de seguridad (Usuario que no existe/no está en el servidor)
    servicio.enviarMensaje(
        user_id=999, 
        server_id=100, 
        channel_id=1001, 
        content="Intento de spam."
    )
    
    servicio.cerrar_conexiones()