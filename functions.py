from datetime import datetime
import pandas as pd

df_festivos = pd.read_excel('./festivos_2024-2025.xlsx')
df_festivos['Fecha'] = pd.to_datetime(df_festivos['Fecha'], format="%d/%m/%Y").dt.date
set_festivos = set(df_festivos['Fecha'].values)

def es_festivo(fecha):
  return fecha in set_festivos

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
  if es_festivo(inicio.date()):
    return 0

  if diasTotales == 1:
    return diferencia_horas(inicio, fin)  
  
  finDiaAjustado = datetime(year= inicio.year, month=inicio.month, day=inicio.day, hour=23, minute=59, second=59)
  return diferencia_horas(inicio, finDiaAjustado)

def calculo_horas_laborales_ultimo_dia(fin):
  if es_festivo(fin.date()):
    return 0
  inicioDiaAjustado = datetime(year= fin.year, month=fin.month, day=fin.day, hour=0)
  return diferencia_horas(inicioDiaAjustado, fin)

def horas_laborales(inicio, fin):
  if inicio >= fin:
    return None
  
  diasTotales =  len(pd.bdate_range(inicio.date(), fin.date()))
  primerDia = calculo_horas_laborales_primer_dia(inicio, fin, diasTotales)
  if diasTotales == 1:
    return primerDia

  ultimoDia = calculo_horas_laborales_ultimo_dia(fin)

  if diasTotales == 2:
    return primerDia + ultimoDia

  festivos = festivos_entre_fechas(inicio, fin)
  return primerDia + ultimoDia + (diasTotales - 2 - festivos) * 8