import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title='ARGUS', layout='wide')
engine=create_engine(os.getenv('DATABASE_URL','postgresql+psycopg2://argus:argus@localhost:5432/argus'))
@st.cache_data(ttl=60)
def load_data():
    return pd.read_sql('''select r.*, concat_ws(' ', s.first_name, s.last_name) as full_name, s.department, p.avg_score, p.attendance_pct, p.failed_courses, p.courses_taken from gold.student_risk_scores r join silver.stg_students s using(student_id) join silver.student_academic_performance p on r.student_id=p.student_id and r.semester=p.semester''', engine)
try:
    df=load_data()
except Exception as exc:
    st.error('ARGUS data is not available yet. Run the pipeline first.')
    st.stop()
st.title('ARGUS')
st.caption('Academic Risk & Guidance Analytics System — human-in-the-loop academic decision support')
a,b,c,d=st.columns(4); a.metric('Students',len(df)); b.metric('High risk',int((df.risk_level=='High').sum())); c.metric('Medium risk',int((df.risk_level=='Medium').sum())); d.metric('Average risk',f'{df.risk_score.mean():.2f}')
x,y=st.columns(2)
with x: st.plotly_chart(px.histogram(df,x='risk_level',title='Risk distribution'),use_container_width=True)
with y: st.plotly_chart(px.scatter(df,x='attendance_pct',y='avg_score',color='risk_level',hover_data=['student_id','full_name'],title='Attendance vs performance'),use_container_width=True)
student=st.selectbox('Student',sorted(df.full_name.unique())); row=df[df.full_name==student].iloc[-1]
a,b,c=st.columns(3); a.metric('Risk level',row.risk_level); b.metric('Risk score',f'{row.risk_score:.2f}'); c.metric('Recommendation',row.recommendation)
st.write('**Risk factors:**',row.risk_reasons)
st.subheader('Institutional risk table')
st.dataframe(df[['student_id','full_name','department','avg_score','attendance_pct','failed_courses','risk_score','risk_level','recommendation','risk_reasons']].sort_values('risk_score',ascending=False),use_container_width=True)
