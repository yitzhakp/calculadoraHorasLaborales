from datetime import datetime, timedelta
import pandas as pd

df_festivos = pd.read_excel('./festivos_2024-2025.xlsx')
df_festivos['Fecha'] = pd.to_datetime(df_festivos['Fecha'], format="%d/%m/%Y").dt.date
set_festivos = set(df_festivos['Fecha'].values)

def es_festivo_o_weekend(fecha):
  return fecha in set_festivos or  fecha.weekday() in [5, 6]

def festivos_entre_fechas(inicio, fin):
  fechaInicio = inicio.date()
  fechaFin = fin.date() 
  return sum(1 for f in set_festivos if fechaInicio < f < fechaFin)

def diferencia_horas(inicio, fin):
  franjas = ((8, 12), (14, 18))
  sumaHoras = 0
  for inicioFranja, finFranja in franjas:
    horaInicioFranja = datetime(year= inicio.year, month=inicio.month, day=inicio.day, hour=inicioFranja)
    horaFinFranja = datetime(year= inicio.year, month=inicio.month, day=inicio.day, hour=finFranja)
    
    if inicio <= horaFinFranja and fin>= horaInicioFranja:
      horaInicioReal = max(horaInicioFranja, inicio)
      horaFinReal = min(horaFinFranja, fin)
      diferenciaHoras = horaFinReal - horaInicioReal
      sumaHoras += diferenciaHoras.seconds / 3600
  return sumaHoras

def calculo_horas_laborales_primer_dia(inicio, fin, diasTotales):
  if es_festivo_o_weekend(inicio.date()):
    return 0

  if diasTotales == 1:
    return diferencia_horas(inicio, fin)
  
  finDiaAjustado = datetime(year= inicio.year, month=inicio.month, day=inicio.day, hour=23, minute=59, second=59)
  return diferencia_horas(inicio, finDiaAjustado)

def calculo_horas_laborales_ultimo_dia(fin):
  if es_festivo_o_weekend(fin.date()):
    return 0
  inicioDiaAjustado = datetime(year= fin.year, month=fin.month, day=fin.day, hour=0)
  return diferencia_horas(inicioDiaAjustado, fin)

def horas_laborales(inicio, fin):
  diasTotales = (fin - inicio).days + 1
  
  laboralesEntreDias =  len(pd.bdate_range(inicio.date() + timedelta(days=1) , fin.date() - timedelta(days=1)))
  primerDia = calculo_horas_laborales_primer_dia(inicio, fin, diasTotales)
  if diasTotales == 1:
    return primerDia

  ultimoDia = calculo_horas_laborales_ultimo_dia(fin)

  if diasTotales == 2:
    return primerDia + ultimoDia

  festivosEntreDias = festivos_entre_fechas(inicio, fin)
  return primerDia + ultimoDia + (laboralesEntreDias - festivosEntreDias) * 8

def get_diff(inicio, fin):
  if inicio >= fin:
    return -horas_laborales(fin, inicio)
  return horas_laborales(inicio, fin)