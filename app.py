#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import mortgage

st.set_page_config(page_title="The Mortgage App",layout='wide')

# Sidebar messages and menus
st.sidebar.header('The Mortgage App')
st.sidebar.write('This app will help you estimate your payments when taking a credit. \
    Start by entering your loan details below.')
principal = st.sidebar.number_input('Debt', value=100000)
interest = st.sidebar.number_input('Interest rate % (APR)', value=3.0)/100
term = st.sidebar.number_input('Term in years', value=10)
rent = st.sidebar.number_input('Monthly rent or income from asset', value=0)
st.sidebar.write(' ')
st.sidebar.write('Note: Please use app only as reference')
st.sidebar.markdown('Author: [**Rene Rivero**](https://www.linkedin.com/in/renejra/)')

# Working out the data
loan = mortgage.Loan(principal=principal, interest=interest, term=term)
am = pd.DataFrame(data=loan._amortize())
am['rent'] = rent
am['payment_mit_miete'] = am.payment - am.rent
am['cum_payment'] = am.payment.expanding().sum()
am['rent'] = am.rent.expanding().sum()
am = am.apply(pd.to_numeric, errors='ignore')
am = am.round(decimals=2)
am['equity'] = am.principal.expanding().sum()
am.rename(columns={'balance':'debt', 'total_interest':'interest_paid'}, inplace=True)

# Rendering app body
st.header('Loan development')

col1, col2, col3 = st.columns([2,1,2])
with col3:
    start = st.date_input('Start Date')
am['date'] = pd.date_range(start, periods=len(am), freq="M")
am.set_index('date', inplace=True)

with col1:
    st.write(' ')
    st.write(f'Monthly Payment: {loan.monthly_payment}')
    if rent != 0:
        st.write(f'...minus generated income: {loan.monthly_payment-rent}')

cols = st.multiselect('Show me some graphs on:', am.columns.to_list(), default=['debt', 'interest_paid', 'equity', 'cum_payment'])
st.markdown('---')
st.line_chart(am[cols])
st.subheader('Amortization plan')
st.write(am)
