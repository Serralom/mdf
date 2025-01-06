import os
import pendulum
import psycopg2


def get_start_of_day():
    spain_tz = pendulum.timezone('Europe/Madrid')
    now = pendulum.now(spain_tz)

    # Si la hora actual es antes de las 9 AM, obtenemos el inicio del día como 9 AM de ayer
    if now.hour < 9:
        start_of_day = now.subtract(days=1).set(hour=9, minute=0, second=0)
    else:
        start_of_day = now.set(hour=9, minute=0, second=0)

    return start_of_day


def init_db():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        dbname=os.getenv('DATABASE_NAME'),
        port=os.getenv('DATABASE_PORT')
    )
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS rachas (
        nombre TEXT,
        fecha_hora TEXT,
        estado TEXT)''')

    conn.commit()
    conn.close()


def init_streak(nombre, juego, tiempo):
    start_of_day = get_start_of_day().to_datetime_string()
    fecha_hora = pendulum.now('Europe/Madrid').to_datetime_string()
    tango_base_date = pendulum.parse('2024-10-08')
    queens_base_date = pendulum.parse('2024-04-30')
    tango_game_number = pendulum.now().diff(tango_base_date).in_days()
    queens_game_number = pendulum.now().diff(queens_base_date).in_days()
    print(f"Nombre: {nombre}, Juego: {juego}, Fecha inicio del día: {start_of_day}")

    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        dbname=os.getenv('DATABASE_NAME'),
        port=os.getenv('DATABASE_PORT')
    )
    c = conn.cursor()

    c.execute('''DELETE FROM public.resultados WHERE nombre = %s AND juego = %s AND fecha_hora >= %s''', (nombre, juego, start_of_day))
    if juego == 'tango':
        c.execute('''INSERT INTO public.resultados (nombre, juego, numero_juego, tiempo, fecha_hora)
            VALUES (%s, %s, %s, %s, %s)''', (nombre, juego, tango_game_number, tiempo, fecha_hora))
    else:
        c.execute('''INSERT INTO public.resultados (nombre, juego, numero_juego, tiempo, fecha_hora)
            VALUES (%s, %s, %s, %s, %s)''', (nombre, juego, queens_game_number, tiempo, fecha_hora))
    conn.commit()

    c.execute('''DELETE FROM public.victorias WHERE numero_juego = %s AND juego = 'tango' ''', (tango_game_number,))
    c.execute('''DELETE FROM public.victorias WHERE numero_juego = %s AND juego = 'queens' ''', (queens_game_number,))
    c.execute('''
        INSERT INTO public.victorias (nombre, juego, numero_juego, tiempo)
        SELECT nombre, juego, numero_juego, tiempo 
        FROM public.resultados
        WHERE numero_juego = %s AND juego = 'queens' 
        AND tiempo = (SELECT MIN(tiempo) FROM public.resultados WHERE numero_juego = %s AND juego = 'queens')
    ''', (queens_game_number, queens_game_number))

    c.execute('''
        INSERT INTO public.victorias (nombre, juego, numero_juego, tiempo)
        SELECT nombre, juego, numero_juego, tiempo 
        FROM public.resultados
        WHERE numero_juego = %s AND juego = 'tango' 
        AND tiempo = (SELECT MIN(tiempo) FROM public.resultados WHERE numero_juego = %s AND juego = 'tango')
    ''', (tango_game_number, tango_game_number))


    conn.commit()
    conn.close()


def get_streaks(juego):
    start_of_day = get_start_of_day().to_datetime_string()

    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        dbname=os.getenv('DATABASE_NAME'),
        port=os.getenv('DATABASE_PORT')
    )
    c = conn.cursor()

    c.execute("SELECT nombre, tiempo FROM public.resultados WHERE fecha_hora >= %s AND juego = %s ORDER BY tiempo ASC", (start_of_day, juego))
    ranking_hoy = c.fetchall()
    conn.close()

    return ranking_hoy


def get_historical_ranking():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        dbname=os.getenv('DATABASE_NAME'),
        port=os.getenv('DATABASE_PORT')
    )
    c = conn.cursor()

    c.execute('''SELECT nombre, COUNT(*) as victorias
        FROM public.victorias
        WHERE juego = 'tango'
        GROUP BY nombre
        ORDER BY victorias DESC''')
    tango_victories = c.fetchall()

    c.execute('''SELECT nombre, COUNT(*) as victorias
        FROM public.victorias
        WHERE juego = 'queens'
        GROUP BY nombre
        ORDER BY victorias DESC''')
    queens_victories = c.fetchall()

    c.execute('''SELECT nombre, COUNT(*) as victorias
        FROM public.victorias
        GROUP BY nombre
        ORDER BY victorias DESC''')
    ranking = c.fetchall()
    conn.close()

    return ranking, tango_victories, queens_victories


def get_top_precoces():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        dbname=os.getenv('DATABASE_NAME'),
        port=os.getenv('DATABASE_PORT')
    )
    c = conn.cursor()

    c.execute('''SELECT MIN(tiempo) FROM public.victorias WHERE juego = 'queens' ''')
    best_queens_time = c.fetchone()[0]
    c.execute('''SELECT MIN(tiempo) FROM public.victorias WHERE juego = 'tango' ''')
    best_tango_time = c.fetchone()[0]
    c.execute('''SELECT nombre FROM public.victorias WHERE juego = 'queens' AND tiempo = %s''', (best_queens_time,))
    best_queens_players = [row[0] for row in c.fetchall()]
    c.execute('''SELECT nombre FROM public.victorias WHERE juego = 'tango' AND tiempo = %s''', (best_tango_time,))
    best_tango_players = [row[0] for row in c.fetchall()]
    conn.close()

    return best_queens_time, best_queens_players, best_tango_time, best_tango_players


def get_average_times():
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        dbname=os.getenv('DATABASE_NAME'),
        port=os.getenv('DATABASE_PORT')
    )
    c = conn.cursor()

    c.execute('''
        SELECT nombre,
               AVG(CASE WHEN juego = 'queens' THEN tiempo END) AS avg_queens,
               AVG(CASE WHEN juego = 'tango' THEN tiempo END) AS avg_tango
        FROM public.resultados
        GROUP BY nombre
    ''')
    average_times = c.fetchall()
    avg_times_dict = {nombre: {"avg_queens": avg_queens, "avg_tango": avg_tango}
                      for nombre, avg_queens, avg_tango in average_times}
    conn.close()

    return avg_times_dict
