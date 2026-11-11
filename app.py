from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from analytics import prepare,summary,category_summary,flags,money,pct
from monthly_tracker import parse_actuals,merge_uploads,detect_outliers,forecast_actuals

st.set_page_config(page_title='Finance Signal Lab',page_icon='📊',layout='wide',initial_sidebar_state='expanded')
ROOT=Path(__file__).resolve().parent
NAV=['Monthly Tracker','Overview','Variance Explorer','Anomaly Monitor','Finance Copilot','About']
COLORS={'actual':'#F4F5FA','budget':'#8D96A8','ink':'#F4F5FA','muted':'#A9B0C0','blue':'#A5B5E6'}
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {color-scheme:dark}
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif;color:#F4F5F8}
.stApp {background:radial-gradient(ellipse 80% 52% at 92% -10%,rgba(72,82,118,.17),transparent 70%),linear-gradient(145deg,#07090F 0%,#10141F 55%,#0A0D15 100%)}
.block-container {padding-top:2rem;padding-bottom:4rem;max-width:1380px}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#111520,#090C13);border-right:1px solid rgba(255,255,255,.09)}
[data-testid="stSidebar"] * {color:#E5E7EF}
[data-testid="stSidebar"] .stButton>button {justify-content:flex-start;text-align:left}
h1,h2,h3,h4 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.045em!important;color:#F9FAFF!important}
h1 {font-size:2.55rem!important;font-weight:700!important}
h2,h3 {font-weight:600!important}
p,li,label,[data-testid="stMarkdownContainer"] {color:#D4D7E0}
[data-testid="stCaptionContainer"],.stCaption {color:#9298AA!important}
[data-testid="stMetric"] {position:relative;overflow:hidden;background:linear-gradient(142deg,rgba(67,73,88,.77) 0%,rgba(35,39,51,.96) 37%,#171C28 100%);border:1px solid rgba(255,255,255,.16);border-radius:24px;padding:22px 23px;box-shadow:0 19px 35px rgba(0,0,0,.30),inset 0 1px 0 rgba(255,255,255,.17),inset 0 -1px 0 rgba(0,0,0,.35);min-height:138px;transition:transform .2s ease,box-shadow .2s ease}
[data-testid="stMetric"]:hover {transform:translateY(-3px);box-shadow:0 24px 40px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.22)}
[data-testid="stMetric"]:before {content:'';position:absolute;left:13%;right:13%;top:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.48),transparent)}
[data-testid="stMetricLabel"] {color:#ADB3C2!important;font-size:.85rem!important}
[data-testid="stMetricValue"] {color:#FAFBFF!important;font-family:'Space Grotesk',sans-serif;font-size:1.7rem!important;letter-spacing:-.04em}
[data-testid="stMetricDelta"] {font-weight:600}
.stButton>button,.stDownloadButton>button {border-radius:13px;border:1px solid rgba(255,255,255,.15);background:linear-gradient(145deg,#303644,#171C27);color:#F2F4FA;box-shadow:0 7px 15px rgba(0,0,0,.23),inset 0 1px 0 rgba(255,255,255,.12);transition:transform .16s ease}
.stButton>button:hover,.stDownloadButton>button:hover {transform:translateY(-2px);background:linear-gradient(145deg,#414859,#242B3A);border-color:rgba(255,255,255,.35);color:white}
.stButton>button[kind="primary"] {background:linear-gradient(135deg,#F7F8FC,#C9CEDB);color:#121722;border:1px solid #F3F5FA;font-weight:700}
.stButton>button[kind="primary"]:hover {background:#FFF;color:#080B11}
[data-testid="stPlotlyChart"] {background:linear-gradient(140deg,#222733,#131824 72%);border:1px solid rgba(255,255,255,.13);border-radius:24px;padding:14px 13px;box-shadow:0 18px 36px rgba(0,0,0,.22),inset 0 1px 0 rgba(255,255,255,.09)}
.note {padding:22px 25px;border:1px solid rgba(255,255,255,.15);background:linear-gradient(140deg,#303543,#171C28);border-radius:22px;margin:14px 0;color:#F1F2F8;box-shadow:0 14px 28px rgba(0,0,0,.22),inset 0 1px 0 rgba(255,255,255,.13)}
.note p {margin-bottom:0}
.kicker {color:#B7BBC9;text-transform:uppercase;letter-spacing:.19em;font-size:.72rem;font-weight:700;margin-bottom:.7rem}
.small {color:#A7ADBE;font-size:.87rem}
[data-testid="stFileUploader"],[data-testid="stExpander"] {background:linear-gradient(145deg,#272C39,#171B25);border:1px solid rgba(255,255,255,.17);border-radius:20px;box-shadow:0 12px 27px rgba(0,0,0,.18)}
[data-testid="stDataFrame"] {border:1px solid rgba(255,255,255,.16);border-radius:17px;overflow:hidden}
[data-testid="stAlert"] {border-radius:16px}
[data-baseweb="select"]>div,[data-testid="stSelectSlider"] {border-radius:12px}
hr {border-color:rgba(255,255,255,.11)!important}
.hero-panel {padding:25px 29px;margin:8px 0 26px;border:1px solid rgba(255,255,255,.17);border-radius:25px;background:radial-gradient(circle at 95% 0%,rgba(255,255,255,.15),transparent 39%),linear-gradient(120deg,#343A49,#171B26 70%);box-shadow:0 22px 45px rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.19)}
.hero-eyebrow {font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:#AEB5C5;font-weight:700}
.hero-title {font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:600;letter-spacing:-.035em;color:#fff;margin:8px 0}
.hero-copy {color:#B8BFCD;font-size:.91rem;max-width:720px}
@media(max-width:760px){h1{font-size:2rem!important}[data-testid="stMetric"]{padding:15px;min-height:110px}.hero-panel{padding:18px}}
</style>''',unsafe_allow_html=True)

@st.cache_data
def load():
    return prepare(pd.read_csv(ROOT/'sample_finance.csv'))

data=load()
if 'page' not in st.session_state: st.session_state.page='Monthly Tracker'
if 'focus_category' not in st.session_state: st.session_state.focus_category='All categories'

def navigate(page,category=None):
    st.session_state.page=page
    if category is not None: st.session_state.focus_category=category
    st.rerun()

def chart_style(fig,height=350):
    fig.update_layout(height=height,margin=dict(l=18,r=18,t=26,b=18),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#D8DBE4',size=12),legend=dict(orientation='h',y=1.16,x=0),hovermode='x unified')
    fig.update_xaxes(showgrid=False, linecolor='#344C6C')
    fig.update_yaxes(gridcolor='rgba(255,255,255,.09)',zerolinecolor='#566070')
    return fig

with st.sidebar:
    st.markdown('### ◈ FINANCE SIGNAL LAB')
    st.caption('Financial intelligence · Portfolio prototype')
    st.divider()
    for p,ico in zip(NAV,['▤','▦','▥','◎','✦','ⓘ']):
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
st.markdown('<div class="hero-panel"><div class="hero-eyebrow">FINANCIAL INTELLIGENCE / INTERACTIVE PROTOTYPE</div><div class="hero-title">See the signals behind the numbers.</div><div class="hero-copy">Explore spending, understand budget gaps, spot unusual patterns and review transparent forecasts — all using synthetic data.</div></div>',unsafe_allow_html=True)

if page=='Monthly Tracker':
    st.title('Monthly Budget Tracker')
    st.caption('Plan vs. actual spending · upload monthly records · review unusual gaps · estimate next months')
    st.info('Demo mode: budget and initial actuals are synthetic. Uploaded actuals replace demo actuals for matching months. No Tesla internal data is used.')
    base=filtered.groupby('month',as_index=False)[['budget_eur','actual_eur']].sum().sort_values('month')
    if base.empty:
        st.warning('No data for these filters.'); st.stop()
    if 'monthly_uploads' not in st.session_state: st.session_state.monthly_uploads={}
    with st.expander('Upload monthly actuals · CSV / Excel',expanded=True):
        st.write('Upload one or more monthly files. Required columns: `month` (YYYY-MM), `actual_eur` (EUR). Optional: `location`, `category`.')
        template=pd.DataFrame({'month':['2026-01','2026-02'],'actual_eur':[125000,132000]})
        st.download_button('↓ Download CSV template',template.to_csv(index=False).encode(),file_name='monthly_actuals_template.csv',mime='text/csv')
        files=st.file_uploader('Monthly actual records',type=['csv','xlsx'],accept_multiple_files=True,help='Only use synthetic or approved non-confidential data.')
        if files:
            try:
                uploaded=merge_uploads(files)
                # Require dimensions when a filtered view would otherwise misattribute totals.
                if (location!='All locations' and 'location' not in uploaded.columns) or (category!='All categories' and 'category' not in uploaded.columns):
                    st.warning('For filtered location/category views, uploaded records must contain the corresponding location/category column. Clear filters or add the columns.')
                else:
                    if 'location' in uploaded.columns and location!='All locations': uploaded=uploaded[uploaded.location==location]
                    if 'category' in uploaded.columns and category!='All categories': uploaded=uploaded[uploaded.category==category]
                    monthly=uploaded.groupby('month',as_index=False)['actual_eur'].sum()
                    base=base.merge(monthly,on='month',how='left',suffixes=('_demo','_uploaded'))
                    base['source']=np.where(base.actual_eur_uploaded.notna(),'Uploaded','Demo')
                    base['actual_eur']=base.actual_eur_uploaded.combine_first(base.actual_eur_demo)
                    base=base[['month','budget_eur','actual_eur','source']]
                    missing=uploaded.loc[~uploaded.month.isin(base.month),'month'].nunique()
                    if missing: st.warning(f'{missing} uploaded month(s) are outside the selected demo budget period and are not shown.')
            except Exception as exc:
                st.error(f'Could not read file: {exc}')
        if 'source' not in base: base['source']='Demo'
        demo_mode=st.toggle('Hide demo actuals (only show uploaded months)',value=False,help='Budget stays visible; months without uploaded actuals have no actual value.')
        if demo_mode: base.loc[base.source!='Uploaded','actual_eur']=np.nan
    threshold=st.slider('Flag unfavorable budget gaps above (%)',5,35,10,1)
    out=detect_outliers(base,threshold)
    observed=out.dropna(subset=['actual_eur'])
    total_budget=float(observed.budget_eur.sum()); total_actual=float(observed.actual_eur.sum())
    total_gap=total_actual-total_budget
    k1,k2,k3,k4=st.columns(4)
    k1.metric('Budget · observed months',money(total_budget))
    k2.metric('Actual · observed months',money(total_actual))
    k3.metric('Gap · observed months',money(total_gap),delta=f'{total_gap/total_budget*100:+.1f}%' if total_budget else None,delta_color='inverse')
    k4.metric('Months requiring review',int((observed.review_flag|observed.statistical_outlier).sum()))
    st.subheader('Monthly planned budget vs. actuals')
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=out.month,y=out.budget_eur,name='Planned budget',mode='lines+markers',line=dict(color='#8D96A8',width=3,dash='dash')))
    fig.add_trace(go.Scatter(x=out.month,y=out.actual_eur,name='Actuals',mode='lines+markers',connectgaps=False,line=dict(color='#F4F5FA',width=3)))
    for _,r in observed.iterrows():
        if r.review_flag or r.statistical_outlier:
            fig.add_trace(go.Scatter(x=[r.month],y=[r.actual_eur],mode='markers',marker=dict(color='#F4F5FA',size=13,symbol='circle-open',line=dict(width=3)),showlegend=False,hovertemplate='Review flagged<extra></extra>'))
    fc=forecast_actuals(out)
    if not fc.empty:
        fig.add_trace(go.Scatter(x=[observed.month.iloc[-1]]+fc.month.tolist(),y=[observed.actual_eur.iloc[-1]]+fc.forecast_eur.tolist(),name='Trend forecast',mode='lines+markers',line=dict(color='#A5B5E6',width=2,dash='dot')))
    st.plotly_chart(chart_style(fig,440),use_container_width=True)
    st.caption('Gray dashed = planned budget · Cyan = recorded actuals · Violet dotted = simple 3-month trend projection. Outlined markers indicate review signals.')
    left,right=st.columns([1.4,1])
    with left:
        st.subheader('Monthly variance and review signals')
        table=out[['month','budget_eur','actual_eur','gap_eur','gap_pct','review_flag','statistical_outlier','source']].copy()
        table['month']=table.month.dt.strftime('%Y-%m')
        st.dataframe(table.rename(columns={'month':'Month','budget_eur':'Budget (€)','actual_eur':'Actual (€)','gap_eur':'Gap (€)','gap_pct':'Gap (%)','review_flag':'Above threshold','statistical_outlier':'Statistical outlier','source':'Source'}),use_container_width=True,hide_index=True)
        st.download_button('↓ Download analysis CSV',table.to_csv(index=False).encode(),file_name='monthly_variance_analysis.csv',mime='text/csv')
    with right:
        st.subheader('Insights')
        if observed.empty:
            st.info('Upload monthly actuals or turn off Hide demo actuals to see insights.')
        else:
            worst=observed.sort_values('gap_eur',ascending=False).iloc[0]
            st.markdown(f'**Largest unfavorable monthly gap:** {worst.month:%b %Y} · {money(worst.gap_eur)} ({pct(worst.gap_pct)}).')
            st.markdown(f'**Review flags:** {int(observed.review_flag.sum())} above threshold; {int(observed.statistical_outlier.sum())} robust statistical outliers.')
            if worst.gap_eur>0: st.write('**Suggested next step:** inspect price, quantity and supplier mix for the flagged month in Variance Explorer.')
            else: st.write('No positive gap in the observed months.')
        st.subheader('Forecast')
        if fc.empty:
            st.info('Forecast needs at least four consecutive months with actuals. No projection shown otherwise.')
        else:
            st.dataframe(fc.assign(month=fc.month.dt.strftime('%Y-%m'),forecast_eur=fc.forecast_eur.round(0)).rename(columns={'month':'Month','forecast_eur':'Projected actual (€)'}),hide_index=True,use_container_width=True)
            st.caption('Simple linear trend extrapolation; not an AI prediction. Illustrative, no confidence interval. Validate against business drivers before use.')
    st.caption('Outliers are review signals, not evidence of errors. Missing actuals are never treated as zero.')

elif page=='Overview':
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
    fig=go.Figure(go.Waterfall(x=['Budget','Price effect','Quantity effect','Actual'],measure=['absolute','relative','relative','total'],y=[s['budget'],filtered.price_variance.sum(),filtered.quantity_variance.sum(),0],connector={'line':{'color':'#5C7395'}},increasing={'marker':{'color':'#F4F5FA'}},decreasing={'marker':{'color':'#4CC9A6'}},totals={'marker':{'color':'#A5B5E6'}},textposition='outside'))
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
