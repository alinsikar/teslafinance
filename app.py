from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from analytics import prepare,summary,category_summary,flags,money,pct

st.set_page_config(page_title='Finance Signal Lab',page_icon='📊',layout='wide',initial_sidebar_state='expanded')
ROOT=Path(__file__).resolve().parent
NAV=['Overview','Variance Explorer','Anomaly Monitor','Finance Copilot','About']
COLORS={'actual':'#D73542','budget':'#8D98A7','ink':'#18212F','muted':'#687487','blue':'#4565A7'}
st.markdown('''<style>
.stApp{background:#F6F8FB;color:#18212F}
.block-container{padding-top:1.65rem;max-width:1350px}
[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E5EAF1}
[data-testid="stMetric"]{background:#FFFFFF;border:1px solid #E6EAF0;border-radius:15px;padding:16px 18px;box-shadow:0 3px 15px rgba(21,33,53,.035)}
[data-testid="stMetricLabel"]{color:#657186}
[data-testid="stMetricValue"]{font-size:1.65rem}
h1,h2,h3{color:#18212F;letter-spacing:-.035em}
.stButton>button[kind="primary"]{background:#D73542;border-color:#D73542}
div[data-testid="stPlotlyChart"]{background:#FFF;border:1px solid #E6EAF0;border-radius:15px;padding:7px}
.note{padding:16px 18px;border:1px solid #E5EAF1;background:#FFF;border-radius:14px;margin:12px 0}
.kicker{color:#7C8796;text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;font-weight:700}
.small{color:#6B7687;font-size:.86rem}
</style>''',unsafe_allow_html=True)

@st.cache_data
def load():
    return prepare(pd.read_csv(ROOT/'sample_finance.csv'))

data=load()
if 'page' not in st.session_state: st.session_state.page='Overview'
if 'focus_category' not in st.session_state: st.session_state.focus_category='All categories'

def navigate(page,category=None):
    st.session_state.page=page
    if category is not None: st.session_state.focus_category=category
    st.rerun()

def chart_style(fig,height=350):
    fig.update_layout(height=height,margin=dict(l=18,r=18,t=26,b=18),paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',font=dict(color='#465268',size=12),legend=dict(orientation='h',y=1.16,x=0),hovermode='x unified')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#EFF2F6',zerolinecolor='#DDE3EB')
    return fig

with st.sidebar:
    st.markdown('### ◈ FINANCE SIGNAL LAB')
    st.caption('Financial intelligence · Portfolio prototype')
    st.divider()
    for p,ico in zip(NAV,['▦','▥','◎','✦','ⓘ']):
        if st.button(f'{ico}  {p}',key='nav_'+p,use_container_width=True,type='primary' if st.session_state.page==p else 'secondary'):
            navigate(p)
    st.divider()
    st.markdown('**GLOBAL FILTERS**')
    locs=['All locations']+sorted(data.location.unique().tolist())
    cats=['All categories']+sorted(data.category.unique().tolist())
    location=st.selectbox('Location',locs)
    months=sorted(data.month.dt.strftime('%Y-%m').unique().tolist())
    period=st.select_slider('Period',options=months,value=(months[0],months[-1]))
    if st.session_state.focus_category not in cats: st.session_state.focus_category='All categories'
    category=st.selectbox('Cost category',cats,key='focus_category')
    st.divider()
    st.caption('DEMO DATA · SYNTHETIC ONLY')
    st.caption('Independent portfolio project. Not affiliated with or endorsed by Tesla.')

filtered=data.copy()
if location!='All locations': filtered=filtered[filtered.location==location]
if category!='All categories': filtered=filtered[filtered.category==category]
filtered=filtered[(filtered.month.dt.strftime('%Y-%m')>=period[0])&(filtered.month.dt.strftime('%Y-%m')<=period[1])]
page=st.session_state.page
st.markdown('<div class="kicker">Finance Signal Lab / '+page+'</div>',unsafe_allow_html=True)

if page=='Overview':
    st.title('Financial Overview')
    st.caption('Understand performance at a glance. Positive cost variance means spending above budget.')
    s=summary(filtered)
    nflags=len(flags(filtered))
    cols=st.columns(4)
    for col,label,value,helptext in zip(cols,['Actual cost','Budget','Budget variance','Flagged records'],[money(s['actual']),money(s['budget']),pct(s['variance_pct']),str(nflags)],['Total actual spending','Total planned spending','Unfavorable when positive','Records above 10% unfavorable variance']):
        col.metric(label,value,help=helptext)
    a,b=st.columns([1.55,1])
    with a:
        st.subheader('Budget vs. actual by category')
        c=category_summary(filtered).sort_values('actual_eur',ascending=False)
        long=c.melt(id_vars='category',value_vars=['budget_eur','actual_eur'],var_name='Type',value_name='EUR')
        long['Type']=long.Type.map({'budget_eur':'Budget','actual_eur':'Actual'})
        fig=px.bar(long,x='category',y='EUR',color='Type',barmode='group',color_discrete_map={'Budget':COLORS['budget'],'Actual':COLORS['actual']},labels={'category':'','EUR':'EUR'})
        fig.update_xaxes(tickangle=-20)
        st.plotly_chart(chart_style(fig),use_container_width=True)
    with b:
        st.subheader('Monthly spending trend')
        m=filtered.groupby('month',as_index=False)[['budget_eur','actual_eur']].sum()
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=m.month,y=m.budget_eur,name='Budget',mode='lines+markers',line=dict(color=COLORS['budget'],dash='dash')))
        fig.add_trace(go.Scatter(x=m.month,y=m.actual_eur,name='Actual',mode='lines+markers',line=dict(color=COLORS['actual'],width=3)))
        st.plotly_chart(chart_style(fig),use_container_width=True)
    cs=category_summary(filtered)
    unfavorable=cs[cs.variance_eur>0]
    if not unfavorable.empty:
        top=unfavorable.iloc[0]
        st.markdown(f'<div class="note"><b>Key finding · {top.category}</b><p>Largest unfavorable category variance: <b>{money(top.variance_eur)}</b> ({pct(top.variance_pct)} vs. budget). Investigate price and quantity effects.</p></div>',unsafe_allow_html=True)
        if st.button('Investigate this variance →',type='primary'): navigate('Variance Explorer',str(top.category))
    else:
        st.info('No unfavorable category-level variance in the selected scope.')

elif page=='Variance Explorer':
    st.title('Variance Explorer')
    st.caption('Explain the difference between planned and actual costs with a reconciled price/quantity bridge.')
    s=summary(filtered)
    c1,c2,c3=st.columns(3)
    c1.metric('Net variance',money(s['variance']))
    c2.metric('Price effect',money(filtered.price_variance.sum()))
    c3.metric('Quantity effect',money(filtered.quantity_variance.sum()))
    st.subheader('Variance bridge')
    fig=go.Figure(go.Waterfall(x=['Budget','Price effect','Quantity effect','Actual'],measure=['absolute','relative','relative','total'],y=[s['budget'],filtered.price_variance.sum(),filtered.quantity_variance.sum(),0],connector={'line':{'color':'#B9C1CD'}},increasing={'marker':{'color':'#D73542'}},decreasing={'marker':{'color':'#2B9C83'}},totals={'marker':{'color':'#4565A7'}},textposition='outside'))
    st.plotly_chart(chart_style(fig,380),use_container_width=True)
    st.subheader('Cost drivers by category')
    d=category_summary(filtered)
    show=d[['category','budget_eur','actual_eur','variance_eur','variance_pct','price_variance','quantity_variance']].rename(columns={'category':'Category','budget_eur':'Budget (€)','actual_eur':'Actual (€)','variance_eur':'Variance (€)','variance_pct':'Variance (%)','price_variance':'Price effect (€)','quantity_variance':'Quantity effect (€)'})
    st.dataframe(show.style.format({k:'{:,.0f}' for k in ['Budget (€)','Actual (€)','Variance (€)','Price effect (€)','Quantity effect (€)']}|{'Variance (%)':'{:+.1f}%'}),use_container_width=True,hide_index=True)
    if len(filtered):
        pe=float(filtered.price_variance.sum()); qe=float(filtered.quantity_variance.sum())
        dominant='price' if abs(pe)>=abs(qe) else 'quantity'
        st.markdown(f'<div class="note"><b>Interpretation</b><p>The net variance is {money(s["variance"])}. In this selection, the larger absolute driver is the <b>{dominant} effect</b>. Positive values increase cost; negative values offset it.</p></div>',unsafe_allow_html=True)
    if st.button('Review flagged transactions →'): navigate('Anomaly Monitor')

elif page=='Anomaly Monitor':
    st.title('Anomaly Monitor')
    st.caption('Rule-based review signals, not predictions, audit findings or evidence of wrongdoing.')
    threshold=st.slider('Unfavorable variance threshold (%)',min_value=5,max_value=35,value=10,step=1)
    f=flags(filtered,threshold)
    a,b,c=st.columns(3)
    a.metric('Flagged records',len(f))
    b.metric('High priority (≥20%)',int((f.variance_pct>=20).sum()))
    c.metric('Largest flagged deviation',pct(float(f.variance_pct.max())) if len(f) else '—')
    st.subheader('Review queue')
    if f.empty:
        st.success('No records exceed the selected threshold.')
    else:
        q=f[['month','location','category','budget_eur','actual_eur','variance_eur','variance_pct','severity']].copy()
        q['month']=q.month.dt.strftime('%Y-%m')
        q.columns=['Month','Location','Category','Budget (€)','Actual (€)','Variance (€)','Variance (%)','Priority']
        st.dataframe(q.style.format({k:'{:,.0f}' for k in ['Budget (€)','Actual (€)','Variance (€)']}|{'Variance (%)':'{:+.1f}%'}),hide_index=True,use_container_width=True)
        st.download_button('Download review queue (CSV)',q.to_csv(index=False).encode('utf-8'),file_name='finance_signal_review_queue.csv',mime='text/csv')
    st.markdown('<div class="note"><b>How flags work</b><p>A record is flagged when (actual cost − budget cost) / budget cost exceeds the selected percentage. High priority means ≥20% unfavorable variance. These are transparent screening rules, not statistical proof of an anomaly.</p></div>',unsafe_allow_html=True)
    if st.button('Investigate variance drivers →'): navigate('Variance Explorer')

elif page=='Finance Copilot':
    st.title('Finance Copilot')
    st.caption('Guided, evidence-based finance questions · No external AI model or API key required.')
    questions=['What is our total budget variance?','Which category has the largest unfavorable variance?','Are price or quantity effects driving costs?','Which records should be reviewed first?']
    question=st.selectbox('Choose a question',questions)
    s=summary(filtered); cs=category_summary(filtered); f=flags(filtered)
    st.markdown('#### Analysis')
    if question==questions[0]:
        answer=f'Actual spending is **{money(s["actual"])}** against a budget of **{money(s["budget"])}**. Net variance is **{money(s["variance"])}** ({pct(s["variance_pct"])}). '+('This is unfavorable because actual costs exceed budget.' if s['variance']>0 else 'This is favorable or on budget.')
        evidence=filtered[['month','location','category','budget_eur','actual_eur','variance_eur']]
    elif question==questions[1]:
        unf=cs[cs.variance_eur>0]
        answer=f'**{unf.iloc[0].category}** has the largest unfavorable category-level variance: **{money(unf.iloc[0].variance_eur)}** ({pct(unf.iloc[0].variance_pct)}).' if len(unf) else 'There is no unfavorable category-level variance in the selected scope.'
        evidence=cs[['category','budget_eur','actual_eur','variance_eur']]
    elif question==questions[2]:
        p=float(filtered.price_variance.sum());q=float(filtered.quantity_variance.sum())
        driver='price' if abs(p)>=abs(q) else 'quantity'
        answer=f'The **price effect** is **{money(p)}** and the **quantity effect** is **{money(q)}**. The larger absolute contribution is from **{driver}**. Their sum reconciles to the net cost variance of **{money(p+q)}**.'
        evidence=filtered[['category','price_variance','quantity_variance','variance_eur']]
    else:
        answer=f'**{len(f)}** records exceed the 10% unfavorable variance review threshold. '+(f'The highest percentage deviation is **{pct(f.iloc[0].variance_pct)}**, for **{f.iloc[0].category}** in **{f.iloc[0].location}** ({f.iloc[0].month:%Y-%m}).' if len(f) else 'No records are currently flagged.')
        evidence=f[['month','location','category','variance_eur','variance_pct']]
    st.markdown('<div class="note">'+answer.replace('**','<b>',1).replace('**','</b>',1)+'</div>',unsafe_allow_html=True) if False else st.info(answer)
    with st.expander('View supporting records'):
        st.dataframe(evidence,use_container_width=True,hide_index=True)
    st.markdown('**Suggested next step**')
    st.write('Validate the selected records and investigate material prices and planned-versus-actual quantities before drawing a causal conclusion.')
    st.caption('This is a deterministic analytics assistant, not an LLM. It does not invent causes or access confidential systems.')

else:
    st.title('About Finance Signal Lab')
    st.markdown('### The challenge')
    st.write('Finance teams need to move from identifying cost changes to understanding the underlying price and quantity effects. This independent prototype demonstrates one possible workflow.')
    st.markdown('### What I built')
    st.write('A lightweight, interactive financial analysis application with transparent variance calculations, rule-based review signals and guided explanations.')
    st.markdown('### Methods & technology')
    st.write('Python · Pandas · Plotly · Streamlit · Budget-to-actual variance bridge · Rule-based screening')
    st.markdown('### Data and limitations')
    st.warning('All financial records are synthetic and illustrative. No real Tesla financial data, proprietary systems, or internal information were used. This project is not affiliated with or endorsed by Tesla.')
    st.write('The Finance Copilot uses deterministic calculations rather than a generative AI model. The review flags are not predictions or audit conclusions.')
    st.markdown('### Future extension')
    st.write('A next iteration could add an LLM grounded in verified query results, authenticated data access, audit trails, and evaluation against analyst-reviewed explanations.')
    st.download_button('Download synthetic sample data',data.assign(month=data.month.dt.strftime('%Y-%m')).to_csv(index=False).encode(),file_name='finance_signal_sample_data.csv',mime='text/csv')

st.divider()
st.caption('Finance Signal Lab · Independent portfolio demonstration · Synthetic financial data only')
