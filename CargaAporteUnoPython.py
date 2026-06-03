# -*- coding: cp1252 -*-
from operator import mul
from pathlib import Path #Uso para rutas de archivos en red
from datetime import date, datetime
import locale
from pickletools import pybytes_or_str
import pandas as pd 

#-----------------------
# CONEXION A SQL SERVER
#-----------------------
servidor = r'LH-GESTIONDOS2'
base_datos = 'ESTUDIOSCOMERCIALES'

# 1. Cadena de conexion limpia para Pyodbc
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={servidor};DATABASE={base_datos};Trusted_Connection=yes'

import urllib
import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text, event

# 2. Cadena codificada para SQLAlchemy
params_quoted = urllib.parse.quote_plus(conn_str)
#engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params_quoted}",pool_pre_ping=True)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params_quoted}",pool_pre_ping=True).execution_options(fast_executemany=True)

# 3. Establecer conexiones
conexion = pyodbc.connect(conn_str) 
conexion.timeout = 300 
cursor = conexion.cursor()
#-----------------------
# FIN CONEXION A SQL SERVER
#-----------------------

#-----------------------
#---INSERCION LOG
#-----------------------
query_log_success = """
INSERT INTO dbo.Log_IDG (NOMBRE_SP, USUARIO, FECHA_EJECUCION, ESTADO, FECHA_PROCESO, MENSAJE, CANTIDAD_REGISTROS)
VALUES (?, ORIGINAL_LOGIN(), GETDATE(), ?, CAST(GETDATE() AS DATE), ?, ?)
"""
#-----------------------
#---FIN INSERCION LOG
#-----------------------



# CONFIGURAR IDIOMA ES
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

rutaOperaciones = Path(r"\\losheroes.losheroes.cl\public2\Usuarios\Contabilidad\5 OTRAS ÁREAS (OPERACIONES-EMISORA)\REPORTES AREAS OPERACIONES")

fechaActual = datetime.now()

#-----------------------
# #----FECHA ACTUAL
# anio = fechaActual.year
# mesNombre = fechaActual.strftime("%B")  
# mesDigito = fechaActual.strftime("%m")
# #----TERMINO FECHA ACTUAL
#-----------------------

#

#-----------------------
#----FECHA MES ANTERIOR
#-----------------------
if fechaActual.month == 1:
    fechaMesAnterior = 12
    anio_anterior = fechaActual.year - 1
    import locale
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
else:
    fechaMesAnterior = fechaActual.month - 1   # Se resta la cantidad de meses a retroceder
    anio_anterior = fechaActual.year

fecha_mes_anterior = datetime(anio_anterior, fechaMesAnterior, 1)


anio = fecha_mes_anterior.year
mesNombre = fecha_mes_anterior.strftime("%B")  # Ejemplo: "mayo"
mesDigito = fecha_mes_anterior.strftime("%m")  # Ejemplo: "05"

#-----------------------
#----TERMINO FECHA MES ANTERIOR
#-----------------------



#---Armado de la ruta con la fecha formateada
rutaAporteUno = rutaOperaciones / f"{anio}" / f"{mesDigito} {mesNombre}" / "Clientes/"  

print(f"Ruta construida: {rutaAporteUno}")



#Buscar Archivo Auxiliar 4161200010*.xlsx en la ruta
archivos_encontrados = list(rutaAporteUno.glob("Auxiliar 4161200010*"))

if archivos_encontrados:
    archivo_especifico = archivos_encontrados[0] 
    
    #--LOG ARCHIVO ENCONTRADO
    cursor.execute(query_log_success, ('Busqueda archivo 4161200010*', 'PROCESADO', 'ARCHIVO ENCONTRADO', '0'))
    conexion.commit()

    print(f"\n\nArchivo encontrado: {archivo_especifico.name}")

    
    
#-----------------------
#-----CARGA A SQL SERVER 
#-----------------------
excel_file = pd.ExcelFile(archivo_especifico)

#Si el nombre de archivo cambia, se debe modificar
sheet_name = [sheet for sheet in excel_file.sheet_names if "4161200010 I UTILIDAD" in sheet]

if sheet_name:
    sheet_name_target = sheet_name[0]

    df_raw = pd.read_excel(archivo_especifico, sheet_name=sheet_name_target, skiprows=1, header=None)
    df_raw = df_raw.dropna(how='all').reset_index(drop=True)
    df_destino = pd.DataFrame()

    # #-----------------------
    # #----PERIODO MES
    # #------------------------

    # periodo_original = df_raw.iloc[:, 2].astype(str).str.strip().str.lower()

    #     # Diccionario infalible para traducir el texto a número de mes
    # meses_dicc = {
    #     'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 
    #     'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 
    #     'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
    # }

    # def limpiar_y_convertir_periodo(texto):
    #     try:
    #         # Caso A: Si viene con guion (ej: 'may-26', 'abr-26', 'mar-2026')
    #         if '-' in texto:
    #             mes_texto, anio_texto = texto.split('-')
    #             mes_texto = mes_texto.strip()
    #             anio_texto = anio_texto.strip()
            
    #             # Si el año viene en 2 dígitos (ej: '26'), lo pasamos a 4 ('2026')
    #             if len(anio_texto) == 2:
    #                 anio_texto = f"20{anio_texto}"
            
    #             # Tomamos las primeras 3 letras del mes para buscar en el diccionario
    #             mes_num = meses_dicc.get(mes_texto[:3])
            
    #             if mes_num:
    #                 return f"{anio_texto}-{mes_num}-01"

    #         # Caso B: Si Excel ya lo leyó como una fecha completa (ej: '2026-05-01 00:00:00')
    #         # Extraemos los primeros 10 caracteres (YYYY-MM-DD)
    #         if len(texto) >= 10 and texto[4] == '-' and texto[7] == '-':
    #             return texto[:10]
            
    #         return None
    #     except:
    #         return None
    # #-----------------------
    # #----FIN PERIODO MES
    # #------------------------


    

    
    df_destino['FOLIO'] = pd.to_numeric(df_raw.iloc[:, 0], errors='coerce').fillna(0).astype('int64').astype(str) # Formato para bigint en bbdd sql
    df_destino['RUT_ENTIDAD'] = df_raw.iloc[:, 1].astype(str).str.strip() # Formato para varchar en bbdd sql
    
    # ----------------------------------------------------
    # TRATAMIENTO PARA EL CAMPO PERIODO
    # ----------------------------------------------------
    # 1. Aseguramos texto limpio, sin espacios y en minúsculas
    periodo_original = df_raw.iloc[:, 2].astype(str).str.strip().str.lower()

    # Diccionario manual para normalizar los meses con texto
    meses_dicc = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 
        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 
        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
    }

    def estandarizar_periodo(texto):
        # Si la celda viene vacía en el Excel
        if not texto or texto in ['nan', 'none', '']:
            return None
        try:
            # Caso A: Si ya viene como fecha completa (ej: '2026-04-01 00:00:00')
            # Extraemos los primeros 10 caracteres para dejarlo como '2026-04-01'
            if len(texto) >= 10 and texto[4] == '-' and texto[7] == '-':
                return texto[:10]

            # Caso B: Si viene con el formato problemático con guion (ej: 'mar-26', 'feb-26')
            if '-' in texto:
                partes = texto.split('-')
                mes_txt = partes[0].strip()
                anio_txt = partes[1].strip()
                
                # Si el año viene en 2 dígitos ('26'), lo pasamos a 4 ('2026')
                if len(anio_txt) == 2:
                    anio_txt = f"20{anio_txt}"
                
                # Buscamos el equivalente numérico del mes usando las 3 primeras letras
                mes_num = meses_dicc.get(mes_txt[:3])
                if mes_num:
                    return f"{anio_txt}-{mes_num}-01"
            
            return None
        except:
            return None

    df_destino['PERIODO'] = periodo_original.apply(estandarizar_periodo).astype(str)
    #df_destino['PERIODO'] = pd.to_datetime(periodo_original.apply(limpiar_y_convertir_periodo), errors='coerce')
    df_destino['RUT_AFILIADO'] = df_raw.iloc[:, 3].astype(str).str.strip()
    df_destino['RENTA'] = pd.to_numeric(df_raw.iloc[:, 4], errors='coerce').fillna(0).astype('int64').astype(str)
    df_destino['APORTE'] = pd.to_numeric(df_raw.iloc[:, 5], errors='coerce').fillna(0).astype('int64').astype(str)
    df_destino['OBS'] = df_raw.iloc[:, 6].astype(str).str.strip()
    df_destino['FECHA'] = fecha_mes_anterior.strftime('%Y-%m-%d') + ' 00:00:00.000'


    # CORRECCIÓN 2: Obtener la cantidad de registros directamente del DataFrame mapeado
    cantidadFilas = len(df_destino)
    print(f"Cantidad de registros listos para insertar: {cantidadFilas}")
    
    #-----------------------
    #---PROCESO DE INSERCIÓN MASIVA 
    #-----------------------
    
    try:
        with engine.begin() as conn:
            
            print("[PROCESO] Limpiando la tabla destino...")
            conn.execute(text("TRUNCATE TABLE [sql].[Aporte_Temp]"))
                
            print("[PROCESO] Inyectando registros masivos a SQL Server por bloques de seguridad...")
            df_destino.to_sql(
                name='Aporte_Temp',     
                con=conn,                
                schema='sql',            
                if_exists='append',      
                index=False,             
                chunksize=30000          # Inserta de a 3,000 filas para evitar bloqueos
            )
            
            # Eliminaria la ultima fila donde suele venir el total
            conn.execute(text("DELETE FROM [sql].[Aporte_Temp] WHERE ISNULL(FOLIO,'') = '' or FOLIO = '0'"))


        # -- LOG CARGA EXITOSA 
        cursor.execute(query_log_success, ('Carga Tabla Aporte_Temp', 'PROCESADO', 'CARGA FINALIZADA', str(cantidadFilas)))
        conexion.commit()

        #-----------------------
        #---EJECUCION SP ACTUALIZA 1PORTEMP
        #-----------------------
        
        
        query_sp = "exec dbo.Etl_Actualiza_1por_tem"
        cursor.execute(query_sp)
        print("   -> Procedimiento ejecutado con éxito.\n")
        conexion.commit()
        
        # -- LOG ACTUALIZACION TEMPORAL
        cursor.execute(query_log_success, ('Actualiza Etl_Actualiza_1por_tem', 'PROCESADO', 'ACTUALIZACION FINALIZADA', 0))
        conexion.commit()


        #-----------------------
        #---EJECUCION SP ACTUALIZA 1POR FINAL
        #-----------------------
        
        
        query_sp = "exec dbo.Etl_Actualiza_1por"
        cursor.execute(query_sp)
        print("   -> Procedimiento ejecutado con éxito.\n")
        conexion.commit()

        # -- LOG ACTUALIZACION TEMPORAL
        cursor.execute(query_log_success, ('Actualiza Etl_Actualiza_1por', 'PROCESADO', 'ACTUALIZACION FINALIZADA', 0))
        conexion.commit()



    except Exception as e:
        print(f"\n[ERROR] Ocurrio un fallo al intentar escribir en la base de datos:")
        print(e)
        
        # -- LOG ERROR EN BASE DE DATOS
        cursor.execute(query_log_success, ('Carga Tabla Aporte_Temp', 'ERROR', f"Fallo al insertar registros: {str(e)[:100]}", '0'))
        conexion.commit()


else:
    print("No se encontró ningún archivo que coincida con el patrón 'Auxiliar 4161200010*.xlsx' en la ruta especificada.")




# if rutaOperaciones.exists():
#     print("¡Conexión exitosa! Listando archivos:")
#     for archivo in rutaOperaciones.iterdir():
#         if archivo.is_file():
#             print(f"- {archivo.name}")
# else:
#     print("No se pudo acceder a la ruta. Verifica la conexión o los permisos.")