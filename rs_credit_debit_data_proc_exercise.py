
# coding: utf-8

# In[ ]:

# OVERVIEW and APPROACH
# This python program separates the matched records from the unmatched ones after reading data from URL.
#
# I had two possible solutions in my mind. The first one was to iterate through the data set and 
# for each record identify if there is matching credit\debit. Write the record to the corresponding output file 
# depending on the condition. For examle, if there is not a matching credit for a debit record then write it to the 
# file for the unmatched.  
# The second approach which I decided to pursue is to use SQL-like features of Pandas\datasets. I used the merge() 
# function to make self-joins in order to match the credits to the debits on the specified fields.  
# This option was less robust\flexible compared to the first option but resulted in a more easily maintainable code.

# Author: Mehmet Emin Turanalp, 12/28/2017

#References\Resources:
#1. https://stackoverflow.com/questions/25685545/sql-how-to-return-rows-from-left-table-not-found-in-right-table
#2. http://nbviewer.jupyter.org/urls/bitbucket.org/hrojas/learn-pandas/raw/master/lessons/03%20-%20Lesson.ipynb
#3. https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_excel.html


# In[39]:

import pandas as pd


# In[40]:

url="https://s3-us-west-1.amazonaws.com/roofstock-test/data+assignment+dataset.xlsx"
df=pd.read_excel(url)


# In[41]:

print('OK!')


# In[42]:

df.dtypes


# In[43]:

#dfs=df.query('Property == "1601 MADISON COURT PALATKA, FL 32177"')
dfs=df.copy()
print('data set size is', len(dfs))


# In[44]:

# Assumption: all debit transactions are the ones with Debit not equal to null (same for credits)
dfs_all_debit=dfs[dfs['Debit'].notnull()]
dfs_all_credit=dfs[dfs['Credit'].notnull()]


# In[45]:

# Join the Credits and Debits tables such that Credits.Credit==Debits.Debit and the other 5 fields are equal. 
# This is the list of matching debits and matching credits
dfs_debit=dfs_all_debit.merge(dfs_all_credit, right_on=('Property','Date','Payee / Payer','Type','Reference','Credit'), left_on=('Property','Date','Payee / Payer','Type','Reference','Debit'), how='inner')
dfs_credit=dfs_all_credit.merge(dfs_all_debit, right_on=('Property','Date','Payee / Payer','Type','Reference','Debit'), left_on=('Property','Date','Payee / Payer','Type','Reference','Credit'), how='inner')
dfs_credit


# In[46]:

# If the desired output is a single list containing all the matching debits and credits then we concatinate
matched=pd.concat([dfs_credit,dfs_debit])


# In[47]:

# We take a set difference of all debits and matched debits(subtract latter from the former). This gives us the unmatched debits: 
# A left-join of all debits with matched debits such that the matched debit is null.
# This is normaly straightforward in SQL(see ref #1) but we can do it in two steps in Python.
# First left-join the two tables such that all rows from the left table (dfs_all_debit) is present in the interim result.
# This means that some of the matching rows in the right table (dfs_debit) are going to be null
#
dfs_debit_leftj=dfs_all_debit.merge(dfs_debit, right_on=('Property','Date','Payee / Payer','Type','Reference','Debit_x'), left_on=('Property','Date','Payee / Payer','Type','Reference','Debit'), how='left')
# In the second step we simply select those rows with the right debit value null.
unmatched_debit=dfs_debit_leftj[dfs_debit_leftj['Debit_x'].isnull()]


# In[48]:

#Repeat above step for credits
dfs_credit_leftj=dfs_all_credit.merge(dfs_credit, right_on=['Property','Date','Payee / Payer','Type','Reference','Credit_x'], left_on=['Property','Date','Payee / Payer','Type','Reference','Credit'], how='left')
unmatched_credit=dfs_credit_leftj[dfs_credit_leftj['Credit_x'].isnull()]
unmatched_credit


# In[50]:

# Write matched records to excel file
writer = pd.ExcelWriter('Matched.xlsx')
matched[matched.columns[0:10]].to_excel(writer,'Sheet1')
writer.save()

# Write unmatched records to excel file
writer = pd.ExcelWriter('UnMatched_Credits.xlsx')
unmatched_credit[unmatched_credit.columns[0:10]].to_excel(writer,'Sheet1')
writer.save()
writer = pd.ExcelWriter('UnMatched_Debits.xlsx')
unmatched_debit[unmatched_debit.columns[0:10]].to_excel(writer,'Sheet1')
writer.save()


# In[ ]:



