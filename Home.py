import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.ticker as mtick
import plotly.express as px
st.set_page_config(page_title="Platform Ad Data",
                   layout="wide",
                   initial_sidebar_state="expanded")
@st.cache_data
def load_data():
    df = pd.read_csv("global_sales_data.csv")
    df.rename(columns={'platform': 'Platform'}, inplace=True)
    return df
  
@st.cache_data
def filter_data(df, country, industry):
    if industry != "All":
        df = df[df["industry"] == industry]
    if country != "All":
        df = df[df["country"] == country]
    return df

df = load_data()

col1, col2, col3, col4, col5 = st.columns([1,1,3,1,1])
with col3:
    st.title("Platform Performance Analysis")
st.divider()
df = pd.read_csv('global_sales_data.csv')
df.rename(columns={'platform': 'Platform'}, inplace=True)


st.sidebar.header("Filters")

country_options = sorted(df['country'].dropna().unique())
selected_country = st.sidebar.selectbox(
    "Country",
    options=["All"] + country_options
)

industry_options = sorted(df['industry'].dropna().unique())
selected_industry = st.sidebar.selectbox(
    "Industry",
    options=["All"] + industry_options
)

if selected_industry != "All":
    df = df[df['industry'] == selected_industry]

if selected_country != "All":
    df = df[df['country'] == selected_country]

platform_palette = {
    "Google Ads": "#7FA6C9",   # dusty blue
    "Meta Ads": "#8FBF9F",     # sage green
    "TikTok Ads": "#E39A8A"    # soft terracotta
}
col1, col2 = st.columns(2)
ad_spend_grouped = df.groupby('Platform')['ad_spend'].sum().reset_index()
with col1:
    m1, m2, m3,m4,m5 = st.columns(5)

    tiktok_roa = df[df['Platform'] == 'TikTok Ads']['ROAS'].median().round(3)
    google_roa = df[df['Platform'] == 'Google Ads']['ROAS'].median().round(3)
    meta_roa = df[df['Platform'] == 'Meta Ads']['ROAS'].median().round(3)
    with m2:
        st.metric("Google ROAS", google_roa, border=True, width="content")

    with m3:
        st.metric("Meta ROAS", meta_roa, border=True, width="content")
    with m4:
        st.metric("TikTok ROAS", tiktok_roa,border=True,width="content")
    st.divider()
    platform_financials = df.groupby("Platform")[["ad_spend", "revenue"]].sum().reset_index()

    fig1, ax1 = plt.subplots(figsize=(8, 6))
    platform_financials.plot(
        x="Platform",
        y=["ad_spend", "revenue"],
        kind="bar",
        ax=ax1,
        color=["#D67A6A", "#6FAF8F"],
        edgecolor="black",
        linewidth=1.2
    )
    ax1.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    plt.setp(ax1.get_xticklabels(), rotation=0, ha='center')
    ax1.set_ylabel("Currency")
    ax1.set_title("Ad Spend vs Revenue by Platform")
    st.pyplot(fig1)

with col2:
    m1, m2, m3,m4, m5 = st.columns(5)

    tiktok_ctr = df[df['Platform'] == 'TikTok Ads']['CTR'].mean().round(3)
    google_ctr = df[df['Platform'] == 'Google Ads']['CTR'].mean().round(3)
    meta_ctr = df[df['Platform'] == 'Meta Ads']['CTR'].mean().round(3)

    with m2:
        st.metric("Google AVG CTR", google_ctr,border=True,width="content")

    with m3:
        st.metric("Meta AVG CTR", meta_ctr, border=True, width="content")
    with m4:
        st.metric("TikTok AVG CTR", tiktok_ctr, border=True, width="content")
    st.divider()
    fig2, ax2 = plt.subplots(figsize=(8,6))
    sns.scatterplot(df,x='impressions',y='clicks',hue='Platform',ax=ax2,palette=platform_palette,edgecolor="black",
    linewidth=0.6,alpha=0.8,s=40)
    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    ax2.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
    ax2.set_title("Impressions vs Clicks by Platform")
    ax2.set_ylabel("Clicks")
    ax2.set_xlabel("Impressions")
    st.pyplot(fig2)
st.divider()
fig3, ax3 = plt.subplots(figsize=(9, 4))
sns.histplot(df,x='ROAS',hue='Platform',element='step',legend=True,palette=platform_palette,ax=ax3)
ax3.set_title("Distribution of ROAS")

st.pyplot(fig3)

st.divider()

grouped = (
    df.groupby("Platform")["ROAS"]
      .agg(Min="min", Max="max",Mean='mean',
          Median="median",
          Median_Absolute_Deviation=lambda x: (x - x.median()).abs().median()
      )
)

skewed_values = df.groupby("Platform")["ROAS"].skew()
skewed_roas = df['ROAS'].skew()
st.write("Pearson’s Moment Skewness for ROAS", skewed_roas)
s1, s2 = st.columns(2)
with s1:
    st.write("Skew by Platform",skewed_values)
with s2:
    st.write("ROAS Volatility",grouped)
st.divider()
cpa_df = df[["Platform", "CPA"]]

fig4, ax4 = plt.subplots(figsize=(6, 2.8))

sns.violinplot(
    data=df,
    x="CPA",
    y="Platform",
    palette=platform_palette,
    inner="quartile",     # shows median + IQR inside the violin
    linewidth=1.2,
    ax=ax4
)

ax4.set_title("CPA Distribution by Platform")
ax4.set_xlabel("Cost per Acquisition")
ax4.set_ylabel("Platform")
ax4.grid(True, axis="both", color="#F0F0F0", linewidth=0.7)
plt.tight_layout()

st.pyplot(fig4)

st.divider()

display_video = df[df["campaign_type"].isin(["Display", "Video"])]
shopping_search = df[df['campaign_type'].isin(["Shopping", "Search"])]

display_video_grouped = (
    display_video.groupby(['Platform', 'campaign_type'], as_index=False)
    .agg(count=('campaign_type', 'count'),total_revenue=('revenue', 'sum'),total_ad_spend=('ad_spend', 'sum'),total_impressions=('impressions', 'sum'))
)
display_video_grouped['Cost Per Impression'] = display_video_grouped['total_ad_spend'] / display_video_grouped['total_impressions']
display_video_grouped['ROI'] = ((display_video_grouped['total_revenue'] - display_video_grouped['total_ad_spend']) / display_video_grouped['total_ad_spend']
                                * 100).map(lambda v: f"{v:.2f}%")
display_video_grouped['total_revenue'] = display_video_grouped['total_revenue'].map(lambda x: f"${int(x):,}")
display_video_grouped['total_ad_spend'] = display_video_grouped['total_ad_spend'].map(lambda x: f"${int(x):,}")
display_video_grouped['total_impressions'] = display_video_grouped['total_impressions'].map(lambda x: f"{int(x):,}")
st.write("Brand Awareness Metrics",display_video_grouped)

st.divider()

shopping_search_grouped = shopping_search.groupby(['Platform','campaign_type'],as_index=False).agg(
        count=('campaign_type', 'count'),
        total_impressions=('impressions', 'sum'),
        total_conversions=('conversions', 'sum'),
        total_revenue=('revenue', 'sum'),
        total_ad_spend=('ad_spend', 'sum')
    )

shopping_search_grouped['acquisition_rate'] = (shopping_search_grouped['total_conversions'] / shopping_search_grouped['total_impressions'] * 100).map(
    lambda v: f"{v:.2f}%")

shopping_search_grouped['ROI'] = ((shopping_search_grouped['total_revenue'] - shopping_search_grouped['total_ad_spend']) / shopping_search_grouped['total_ad_spend'] * 100).map(
    lambda v: f"{v:.2f}%")
shopping_search_grouped['total_impressions'] = shopping_search_grouped['total_impressions'].map(lambda x: f"{int(x):,}")
shopping_search_grouped['total_conversions'] = shopping_search_grouped['total_conversions'].map(lambda x: f"{int(x):,}")
shopping_search_grouped['total_revenue'] = shopping_search_grouped['total_revenue'].map(lambda x: f"${int(x):,}")
shopping_search_grouped['total_ad_spend'] = shopping_search_grouped['total_ad_spend'].map(lambda x: f"${int(x):,}")
st.write("Audience Acquisition Metrics",shopping_search_grouped)

st.divider()

country_industry = df.groupby(["country","industry"]).agg(
    total_spend=("ad_spend", "sum"),
    total_revenue=("revenue", "sum")
).reset_index()

country_industry['total_spend'] = country_industry['total_spend'].round(0)

country_industry["ROI"] = (((country_industry["total_revenue"] - country_industry["total_spend"]) / country_industry["total_spend"]) * 100).round(0)

fig1 = px.sunburst(
    country_industry,
    path=['country', 'industry'],
    values='total_spend',
    color='ROI',
    color_continuous_scale="RdBu",
    hover_data={'ROI': ':.2f','total_spend': ':,.0f'},
)
fig1.update_traces(textinfo="label+value+percent entry")
fig1.update_layout(title={'text': "Ad Spend and ROI by Country and Industry", "x":0.5,"y": 1,'xanchor': 'center',
        'yanchor': 'top'}, title_font_size=24,
    width=650,
    height=650,
    margin=dict(t=40, l=0, r=0, b=0)
)


st.caption("Click on a country segment on the chart to filter")
st.plotly_chart(fig1, use_container_width=True)
