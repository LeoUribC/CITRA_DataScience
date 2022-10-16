import pandas as pd
import numpy as np
from datetime import datetime

# lectura inicial de los datos en bruto
datosContaminantes = pd.read_csv("CSV_Datos_OK.csv", parse_dates={"Fecha":["Año", "Mes", "Día"]})
datosContaminantes = datosContaminantes.drop(["Minuto", "Segundo"], axis=1)

# --------------------------------------------------
# limpieza y organizacion general de los datos
# --------------------------------------------------

# obtener las semanas, los años, los dias y los meses para cada año
def getWeek(df):
    return int( df.strftime('%W') )

def getYear(df):
    return df.year

def getDay(df):
    return df.day

def getMonth(df):
    return df.month

# Funcion para convertir valores str en float
def ToFloat(df):
    if isinstance(df, str):
        if df.count('.') == 2:
            return float( df.replace('.', '', 1) )
        else:
            return float(df)
    else:
        return float(df)

# Funcion para extraer los dias de la semana
def DayOfWeek(df):
    return df.strftime('%A')

# funcion para concatenar dos listas, elemento a elemento
def addLists(firstList, secondList):
    finalList= []
    for i in range( len(firstList) ):
        finalList.append( str(firstList[i]) + '-' + str(secondList[i]) )
    return finalList

# Reemplazando valores en la columna a aplicar la funcion ToFloat
datosContaminantes["valor_contaminante"] = datosContaminantes["valor_contaminante"].apply(ToFloat)

# insertando los dias
datosContaminantes.insert(1, "Dia_Semana", np.array( datosContaminantes["Fecha"].apply(DayOfWeek) ) )

# eliminando valores no permitidos
datosContaminantes = datosContaminantes[(datosContaminantes["valor_contaminante"] >= 0.0) & \
                                        (datosContaminantes["valor_contaminante"] != 999.0) & \
                                        (datosContaminantes["calidad_contaminante"] != 151)]

# ordenando
datosContaminantes = datosContaminantes.sort_values(by=["Fecha", "Hora"]).reset_index().drop("index", axis=1)

datosContaminantes.insert( 1, "año", datosContaminantes["Fecha"].apply(getYear) )
datosContaminantes.insert( 1, "mes", datosContaminantes["Fecha"].apply(getMonth) )
datosContaminantes.insert( 1, "semana", datosContaminantes["Fecha"].apply(getWeek) )
datosContaminantes.insert( 1, "dia", datosContaminantes["Fecha"].apply(getDay) )


# -------------------------------------
# obtencion de los promedios
# -------------------------------------

estaciones = datosContaminantes["estacion"].unique()
contaminantes = datosContaminantes["contaminante"].unique()
semanas = np.sort( datosContaminantes["semana"].unique() )
meses = datosContaminantes["mes"].unique()
years = datosContaminantes["año"].unique()

promedio_semana = [];  newYears = [];  newSemanas = [];  newEstaciones = [];  newContaminantes = []

for year in years:
    for semana in semanas:
        for estacion in estaciones:
            for contaminante in contaminantes:
                promedio_semana.append(
                    np.mean(
                        datosContaminantes[
                            (datosContaminantes["año"] == year) & \
                            (datosContaminantes["semana"] == semana) & \
                            (datosContaminantes["estacion"] == estacion) & \
                            (datosContaminantes["contaminante"] == contaminante)
                        ]["valor_contaminante"]
                    )
                )
            newContaminantes += list(contaminantes)
            newEstaciones += len(contaminantes)*[estacion]
            newSemanas += len(contaminantes)*[semana]
            newYears += len(contaminantes)*[year]

# funcion para concatenar dos listas, elemento a elemento
# usada para obtener año-mes
def addLists(firstList, secondList):
    finalList= []
    for i in range( len(firstList) ):
        finalList.append( str(firstList[i]) + '-' + str(secondList[i]) )
    return finalList

promedioSemanalContaminantes = {
    "fecha":addLists(newYears, newSemanas),
    "año":newYears,
    "semana":newSemanas,
    "estacion":newEstaciones,
    "contaminante":newContaminantes,
    "promedio_contaminante":promedio_semana
}

# creacion de dataframe
promedioSemanalContaminantes_df = pd.DataFrame(data=promedioSemanalContaminantes)
promedioSemanalContaminantes_df = promedioSemanalContaminantes_df.dropna()

# ordenando
promedioSemanalContaminantes_df = promedioSemanalContaminantes_df.sort_values(by=['año', 'semana']).reset_index().drop("index", axis=1)

# exportando a csv (descomentar para crear el .csv)
promedioSemanalContaminantes_df.to_csv('promedioSemanalContaminantes.csv')