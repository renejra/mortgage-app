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
start = st.sidebar.date_input('Start Date')

st.sidebar.write('Note: Please use app only as reference')
st.sidebar.markdown('Author: [**Rene Rivero**](https://www.linkedin.com/in/renejra/)')

# Working out the data
loan = mortgage.Loan(principal=principal, interest=interest, term=term)
am = pd.DataFrame(data=loan._amortize())
am['income'] = rent
am['cashflow'] = am.income - am.payment
am['cum_cashflow'] = am['cashflow'].expanding().sum()
am['cum_payment'] = am.payment.expanding().sum()
am['income'] = am.income.expanding().sum()
am = am.apply(pd.to_numeric, errors='ignore')
am = am.round(decimals=2)
am['equity'] = am.principal.expanding().sum()
am.rename(columns={'balance':'debt', 'total_interest':'interest_paid'}, inplace=True)

# Graph results
st.header('Loan Development Summary')
am['date'] = pd.date_range(start, periods=len(am), freq="M")
am.set_index('date', inplace=True)
cols = st.multiselect('Select properties to graph:', 
                      am.columns.to_list(), 
                      default=['debt', 'interest_paid', 'equity', 'cum_payment', 'income'])
st.line_chart(am[cols])

# Metrics and amortization
st.header("Metrics")
col1, col2 = st.columns(2)
with col1:
    st.metric('Principal (loan amount):', '{}{:>11,}'.format(loan._currency,loan.principal))
    st.metric('APR (Interest):', '{:>11} %'.format(loan.apr))
    st.metric('Monthly Payment:', '{}{:>11}'.format(loan._currency,loan.monthly_payment))
    st.metric('Total interest payments:','{}{:>11,}'.format(loan._currency,loan.total_interest))
    if rent > 0:
        st.metric('Monthly Income:', '{}{:>11}'.format(loan._currency,rent))
        st.metric('Monthly Cashflow:', '{}{:>11}'.format(loan._currency,rent - loan.monthly_payment))

with col2:
    st.metric('Term:', '{:>11} {}'.format(loan.years_to_pay, loan.term_unit))
    st.metric('APY (Interest):', '{:>11} %'.format(loan.apy))
    st.metric('Total payments:','{}{:>11,}'.format(loan._currency,loan.total_paid))
    st.metric('Interest to principal:','{:>11} %'.format(loan.interest_to_principle))
    if rent > 0:
        st.metric('Total income:','{}{:>11,}'.format(loan._currency,am.income[-1]- am.income[0]))
        st.metric('Cumulated Cashflow:', '{}{:>11}'.format(loan._currency, am["cum_cashflow"].iloc[-1]))
        st.metric('Income to principal:','{:>11} %'.format((am.income[-1]- am.income[0])*100/principal))

st.subheader('Amortization plan')
st.write(am.loc[:, am.columns != 'cashflow'])