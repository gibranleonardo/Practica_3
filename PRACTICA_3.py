# PRACTICA_3.py

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CARGA DE DATOS
# -------------------------
fact = pd.read_csv("FactSale.csv")
city = pd.read_csv("DimCity.csv")
city["City Key"] = city["City Key"].astype(int)

customer = pd.read_csv("DimCustomer.csv")
customer.columns = customer.iloc[0]  # usar la fila real del header
customer = customer.drop(index=0)
customer = customer.rename(columns=lambda x: str(x).strip())
customer["Customer Key"] = customer["Customer Key"].astype(int)

date = pd.read_csv("DimDate.csv")
date["Date"] = pd.to_datetime(date["Date"])

employee = pd.read_excel("DimEmployee.xlsx")
employee["Employee Key"] = employee["Employee Key"].astype(int)

stock = pd.read_csv("DimStockItem.csv")
stock.columns = stock.iloc[0]  # usar la fila real del header
stock = stock.drop(index=0)
stock = stock.rename(columns=lambda x: str(x).strip())
stock["Stock Item Key"] = stock["Stock Item Key"].astype(int)

fact["Delivery Date Key"] = pd.to_datetime(fact["Delivery Date Key"])

# -------------------------
# UNIFICACIÓN DE DATOS
# -------------------------
date["Date"] = pd.to_datetime(date["Date"])
fact["Delivery Date Key"] = pd.to_datetime(fact["Delivery Date Key"])

merged = fact.merge(city, on="City Key", how="left")
merged = merged.merge(customer, on="Customer Key", how="left")
merged = merged.merge(date, left_on="Delivery Date Key", right_on="Date", how="left")
merged = merged.merge(employee, left_on="Salesperson Key", right_on="Employee Key", how="left")
merged = merged.merge(stock, on="Stock Item Key", how="left", suffixes=('', '_stock'))

# -------------------------
# INTERFAZ DE USUARIO
# -------------------------
st.title("Sales Report")

# FILTROS
def safe_selectbox(label, options):
    return st.selectbox(label, options) if len(options) > 0 else None

province = st.selectbox("Select State Province:", ["All"] + sorted(merged["State Province"].dropna().unique().tolist()))
buying_group = st.selectbox("Select Buying Group:", ["All"] + sorted(merged["Buying Group"].dropna().unique().tolist()))
empleado = st.selectbox("Select Employee:", ["All"] + sorted(merged["Employee"].dropna().unique().tolist()))
# fecha = safe_selectbox("Select Date:", merged["Date"].dropna().dt.date.unique())

# Validación del filtro
df_filtros = merged.copy()
if province and province != "All": df_filtros = df_filtros[df_filtros["State Province"] == province]
if buying_group and buying_group != "All": df_filtros = df_filtros[df_filtros["Buying Group"] == buying_group]
if empleado and empleado != "All": df_filtros = df_filtros[df_filtros["Employee"] == empleado]
# if fecha: df_filtros = df_filtros[df_filtros["Date"].dt.date == fecha]

# -------------------------
# KPIs
# -------------------------
st.subheader("KPI Cards")
kpi1 = df_filtros["Profit"].mean()
kpi2 = df_filtros["Profit"].max()
kpi3 = df_filtros["Profit"].min()
kpi4 = df_filtros["Unit Price"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Profit", f"${kpi1:,.2f}")
col2.metric("Maximum Profit", f"${kpi2:,.2f}")
col3.metric("Minimum Profit", f"${kpi3:,.2f}")
col4.metric("Avgerage Unit Price", f"${kpi4:,.2f}")

# -------------------------
# GRÁFICAS
# -------------------------
st.subheader("Visualizations")

# 1. LÍNEA: Total Profit on 2016
profit_2016 = df_filtros[df_filtros["Calendar Year"] == 2016] 
profit_by_date = profit_2016.groupby("Date")["Profit"].sum().reset_index()
fig1 = px.line(profit_by_date, x="Date", y="Profit", title="Total Profit on 2016")
st.plotly_chart(fig1)

# 2. DONA: Avg Unit Price by State Province
prov_avg = df_filtros[~df_filtros["State Province"].isna()].groupby("State Province")["Unit Price"].mean().reset_index()
fig2 = px.pie(prov_avg, values="Unit Price", names="State Province", hole=0.4, title="Average Unit Price by State Province")
st.plotly_chart(fig2)

# 3. COLUMNAS: Avg Unit Price by Employee
emp_avg = df_filtros.groupby("Employee")["Profit"].mean().reset_index()
emp_avg = emp_avg.sort_values(by="Profit", ascending=False)
fig3 = px.bar(emp_avg, x="Employee", y="Profit", title="Average Profit by Employee")
st.plotly_chart(fig3)

# 4. BARRAS: Sale Key by Buying Group (sin filtros locales para mostrar todos los grupos)
sale_group_all = df_filtros.groupby("Buying Group")["Sale Key"].count().reset_index()
sale_group_all = sale_group_all.sort_values(by="Sale Key", ascending=True)
fig4 = px.bar(sale_group_all, x="Sale Key", y="Buying Group", orientation='h', title="Sale Key by Buying Group")
st.plotly_chart(fig4)

# -------------------------
# NOTA FINAL
# -------------------------
# st.info("Práctica 3 - ITESO - Laboratorio de Visualización de Datos Financieros" )
