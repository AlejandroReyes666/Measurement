import mysql.connector
import random
import time

try:
    # Conectar a la base de datos
    conn = mysql.connector.connect(host="localhost", user="root", password="March0208", database="medicionesdb")
    cursor = conn.cursor()

    if conn.is_connected():
        print("✅ Conexión establecida con éxito")

    # 1️⃣ Verificar si hay ubicaciones registradas
    cursor.execute("SELECT id FROM ubicaciones")
    ubicaciones_validas = [row[0] for row in cursor.fetchall()]

    # Si no hay ubicaciones, creamos una por defecto
    if not ubicaciones_validas:
        print("⚠️ No hay ubicaciones en la base de datos. Creando una ubicación por defecto...")
        cursor.execute("INSERT INTO ubicaciones (nombre) VALUES (%s)", ("Ubicación 1",))
        conn.commit()
        cursor.execute("SELECT id FROM ubicaciones")  # Volvemos a consultar
        ubicaciones_validas = [row[0] for row in cursor.fetchall()]
        print(f"✅ Ubicación creada con ID: {ubicaciones_validas[0]}")

    ubicacion_id = ubicaciones_validas[0]  # Usar la primera ubicación válida

    # 2️⃣ Verificar si hay dispositivos registrados
    cursor.execute("SELECT id FROM dispositivos")
    dispositivos_validos = [row[0] for row in cursor.fetchall()]

    # Si no hay dispositivos, creamos algunos automáticamente
    if not dispositivos_validos:
        print("⚠️ No hay dispositivos en la base de datos. Creando dispositivos de prueba...")
        for i in range(1, 11):  # Creamos 3 dispositivos
            cursor.execute("INSERT INTO dispositivos (nombre, ubicacion_id, estado) VALUES (%s, %s, %s)", 
                           (f"Dispositivo_{i}", ubicacion_id, "activo"))  # Asignamos una ubicación válida
            conn.commit()
        
        # Volvemos a consultar los dispositivos creados
        cursor.execute("SELECT id FROM dispositivos")
        dispositivos_validos = [row[0] for row in cursor.fetchall()]
        print(f"✅ Dispositivos creados: {dispositivos_validos}")

    print(f"📌 Dispositivos válidos encontrados: {dispositivos_validos}")

    # 3️⃣ Simulación de mediciones
    sensores = ["temperatura", "voltaje", "distancia", "nivel", "luminocidad"]
    generate = True
    counter = 0

    while generate:
        dispositivo_id = random.choice(dispositivos_validos)  # Elegir solo IDs válidos


        valores_sensores = {sensor: round(random.uniform(0, 100), 2) for sensor in sensores}
        # Construir la consulta SQL dinámicamente
        columnas = ", ".join(valores_sensores.keys())  # Convierte la lista en un string separado por comas
        valores_placeholder = ", ".join(["%s"] * len(valores_sensores))  # "%s, %s, %s, %s, %s"
        valores = list(valores_sensores.values())  # Obtener solo los valores

        try:
            query = f"INSERT INTO mediciones_diarias (dispositivo_id, {columnas}, fecha) VALUES (%s, {valores_placeholder}, NOW())"
            cursor.execute(query, [dispositivo_id] + valores)
            conn.commit()
            print(f"✅ Insertado en dispositivo {dispositivo_id}: {valores_sensores}")
                  
        except mysql.connector.Error as e:
            print(f"❌ Error al insertar datos: {e}")

        counter += 1
        print(f"📊 La cuenta va en {counter}")

        if counter == 1000:
            generate = False

        time.sleep(5)  # Esperar 5 segundos antes de la siguiente medición

except mysql.connector.Error as e:
    print(f"❌ Error de conexión: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("🔒 Conexión cerrada")
