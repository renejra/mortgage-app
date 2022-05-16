#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import mortgage

st.set_page_config(page_title="The Mortgage App",layout='wide')

# Sidebar messages and menus
st.sidebar.header('The Mortgage App')
st.sidebar.write('This app will help you estimate your payments when taking a credit. Start by entering your loan details below.')
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
am['income'] = rent
am['payment_w_income'] = am.payment - am.income
am['cum_payment'] = am.payment.expanding().sum()
am['income'] = am.income.expanding().sum()
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

cols = st.multiselect('Show me some graphs on:', am.columns.to_list(), default=['debt', 'interest_paid', 'equity', 'cum_payment', 'income'])
st.markdown('---')
st.line_chart(am[cols])
st.subheader('Amortization plan')
st.write(am.loc[:, am.columns != 'payment_w_income'])

st.header('Summary')
col1, col2 = st.columns(2)
with col1:
    st.write('Original Balance:         {}{:>11,}'.format(loan._currency,loan.principal))
    st.write('Interest Rate:             {:>11} %'.format(loan.interest))
    st.write('APY:                       {:>11} %'.format(loan.apy))
    st.write('APR:                       {:>11} %'.format(loan.apr))
    st.write('Term:                      {:>11} {}'.format(loan.term, loan.term_unit))
    st.write('Monthly Payment:          {}{:>11}'.format(loan._currency,loan.monthly_payment))

with col2:
    st.write('Total principal payments: {}{:>11,}'.format(loan._currency,loan.total_principal))
    st.write('Total interest payments:  {}{:>11,}'.format(loan._currency,loan.total_interest))
    st.write('Total interest payments:  {}{:>11,}'.format(loan._currency,loan.total_interest))
    st.write('Total income:             {}{:>11,}'.format(loan._currency,am.income[-1]- am.income[0]))
    st.write('Total payments:           {}{:>11,}'.format(loan._currency,loan.total_paid))
    st.write('Interest to principal:     {:>11} %'.format(loan.interest_to_principle))
    st.write('Income to principal:       {:>11} %'.format((am.income[-1]- am.income[0])*100/principal))
    st.write('Years to pay:              {:>11}'.format(loan.years_to_pay))