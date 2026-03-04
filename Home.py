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

with tab2:
    # Always use full unfiltered data for the strategic summary
    df_full = df.copy()

    st.markdown("## Strategic Intelligence Report")
    st.markdown("*Full dataset · 1,800 campaigns · 3 platforms · 7 countries · 5 industries*")
    st.divider()

    # ── KPI Headline Row ──────────────────────────────────────────────────
    total_spend = df_full['ad_spend'].sum()
    total_revenue = df_full['revenue'].sum()
    blended_roi = (total_revenue - total_spend) / total_spend * 100

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Ad Spend", f"${total_spend/1e6:.1f}M")
    k2.metric("Total Revenue", f"${total_revenue/1e6:.1f}M")
    k3.metric("Blended ROI", f"{blended_roi:.0f}%")
    k4.metric("Avg ROAS", f"{df_full['ROAS'].mean():.2f}x")

    st.divider()

    # ── Section 1: Platform ROI Comparison ───────────────────────────────
    st.markdown("### Platform Return on Investment")

    pf = df_full.groupby('Platform')[['ad_spend', 'revenue']].sum().reset_index()
    pf['ROI'] = ((pf['revenue'] - pf['ad_spend']) / pf['ad_spend'] * 100).round(1)
    pf['Budget Share'] = (pf['ad_spend'] / pf['ad_spend'].sum() * 100).round(1)
    pf['Median ROAS'] = df_full.groupby('Platform')['ROAS'].median().round(2).values
    pf['Median CPA'] = df_full.groupby('Platform')['CPA'].median().round(2).values
    pf['Avg CTR'] = (df_full.groupby('Platform')['CTR'].mean() * 100).round(2).values

    col_chart, col_table = st.columns([1.4, 1])

    with col_chart:
        roi_colors = ["#7FA6C9", "#8FBF9F", "#E39A8A"]
        fig_roi, ax_roi = plt.subplots(figsize=(7, 4))
        bars = ax_roi.barh(pf['Platform'], pf['ROI'], color=roi_colors, edgecolor='white', height=0.5)
        for bar, val in zip(bars, pf['ROI']):
            ax_roi.text(bar.get_width() + 8, bar.get_y() + bar.get_height() / 2,
                        f"{val:.0f}%", va='center', fontsize=11, color='#333333', fontweight='bold')
        ax_roi.set_xlabel("ROI (%)", fontsize=10)
        ax_roi.set_title("ROI by Platform", fontsize=13, fontweight='bold', pad=12)
        ax_roi.spines[['top', 'right', 'left']].set_visible(False)
        ax_roi.tick_params(axis='y', labelsize=11)
        ax_roi.set_xlim(0, pf['ROI'].max() * 1.18)
        ax_roi.grid(axis='x', color='#EEEEEE', linewidth=0.8)
        plt.tight_layout()
        st.pyplot(fig_roi)

    with col_table:
        display_pf = pf[['Platform', 'Budget Share', 'ROI', 'Median ROAS', 'Avg CTR', 'Median CPA']].copy()
        display_pf['Budget Share'] = display_pf['Budget Share'].map(lambda x: f"{x}%")
        display_pf['ROI'] = display_pf['ROI'].map(lambda x: f"{x}%")
        display_pf['Median ROAS'] = display_pf['Median ROAS'].map(lambda x: f"{x}x")
        display_pf['Avg CTR'] = display_pf['Avg CTR'].map(lambda x: f"{x}%")
        display_pf['Median CPA'] = display_pf['Median CPA'].map(lambda x: f"${x}")
        st.dataframe(display_pf.set_index('Platform'), use_container_width=True, height=175)
        st.caption(
            "⚠️ TikTok receives only 24% of budget yet delivers 662% ROI — "
            "the highest of any platform. Google holds 57% of spend at the lowest return."
        )

    st.divider()

    # ── Section 2: Campaign Type Breakdown ───────────────────────────────
    st.markdown("### Campaign Type Performance")

    ct = df_full.groupby(['Platform', 'campaign_type']).agg(
        total_spend=('ad_spend', 'sum'),
        total_revenue=('revenue', 'sum'),
        total_conversions=('conversions', 'sum'),
        total_impressions=('impressions', 'sum')
    ).reset_index()
    ct['ROI'] = ((ct['total_revenue'] - ct['total_spend']) / ct['total_spend'] * 100).round(1)

    fig_ct, ax_ct = plt.subplots(figsize=(10, 4.5))
    campaign_types = ct['campaign_type'].unique()
    platforms = ['Google Ads', 'Meta Ads', 'TikTok Ads']
    x = range(len(campaign_types))
    width = 0.25
    bar_colors = {"Google Ads": "#7FA6C9", "Meta Ads": "#8FBF9F", "TikTok Ads": "#E39A8A"}

    for i, platform in enumerate(platforms):
        subset = ct[ct['Platform'] == platform].set_index('campaign_type').reindex(campaign_types)
        offset = (i - 1) * width
        bars = ax_ct.bar([xi + offset for xi in x], subset['ROI'], width=width - 0.02,
                         color=bar_colors[platform], label=platform, edgecolor='white')

    ax_ct.set_xticks(list(x))
    ax_ct.set_xticklabels(campaign_types, fontsize=11)
    ax_ct.set_ylabel("ROI (%)", fontsize=10)
    ax_ct.set_title("ROI by Campaign Type & Platform", fontsize=13, fontweight='bold', pad=12)
    ax_ct.legend(fontsize=9)
    ax_ct.spines[['top', 'right']].set_visible(False)
    ax_ct.grid(axis='y', color='#EEEEEE', linewidth=0.8)
    ax_ct.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}%'))
    plt.tight_layout()
    st.pyplot(fig_ct)

    st.caption(
        "TikTok Search (712% ROI) is the single best-performing campaign-platform combination. "
        "Google Display (216%) is the weakest — consuming budget at the lowest rate of return."
    )

    st.divider()

    # ── Section 3: Geo / Industry Heatmap ────────────────────────────────
    st.markdown("### Geographic & Industry ROI Matrix")

    ci = df_full.groupby(['country', 'industry']).agg(
        total_spend=('ad_spend', 'sum'), total_revenue=('revenue', 'sum')
    ).reset_index()
    ci['ROI'] = ((ci['total_revenue'] - ci['total_spend']) / ci['total_spend'] * 100).round(1)
    heatmap_data = ci.pivot(index='country', columns='industry', values='ROI')

    fig_hm, ax_hm = plt.subplots(figsize=(9, 5))
    sns.heatmap(
        heatmap_data, annot=True, fmt=".0f", cmap="RdYlGn",
        linewidths=0.5, linecolor='white', ax=ax_hm,
        cbar_kws={'label': 'ROI (%)'}
    )
    ax_hm.set_title("ROI % by Country & Industry", fontsize=13, fontweight='bold', pad=12)
    ax_hm.set_xlabel("")
    ax_hm.set_ylabel("")
    plt.xticks(rotation=20, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    st.pyplot(fig_hm)

    geo_col1, geo_col2 = st.columns(2)
    with geo_col1:
        st.markdown("**🟢 Top 5 Performers**")
        top5 = ci.sort_values('ROI', ascending=False).head(5)[['country', 'industry', 'ROI']].copy()
        top5['ROI'] = top5['ROI'].map(lambda x: f"{x:.1f}%")
        st.dataframe(top5.reset_index(drop=True), use_container_width=True, hide_index=True)
    with geo_col2:
        st.markdown("**🔴 Bottom 5 Performers**")
        bot5 = ci.sort_values('ROI', ascending=True).head(5)[['country', 'industry', 'ROI']].copy()
        bot5['ROI'] = bot5['ROI'].map(lambda x: f"{x:.1f}%")
        st.dataframe(bot5.reset_index(drop=True), use_container_width=True, hide_index=True)

    st.divider()

    # ── Section 4: Strategic Recommendations ────────────────────────────
    st.markdown("### Strategic Recommendations")

    recs = [
        ("🔁", "Rebalance Budget Toward TikTok",
         "TikTok delivers 662% ROI with the lowest CPA ($22.22) yet holds only 24% of total spend. "
         "Shifting 15–20% of Google's budget to TikTok could materially improve blended returns."),
        ("🔍", "Audit Google Ads Display Campaigns",
         "At 216% ROI and a $48.25 median CPA, Google Display is the weakest investment in the portfolio. "
         "Pause or restructure in favour of Google Search (292% ROI), where intent-targeting works."),
        ("📈", "Scale Canada E-commerce & India EdTech",
         "Both combinations exceeded 530% ROI. Increasing spend with localized creative and seasonal "
         "campaigns in these markets represents clear upside."),
        ("🇺🇸", "Investigate US Market Performance",
         "All five US industry combinations rank in the bottom tier (253–319% ROI). A full creative, "
         "keyword, and competitive audit is recommended before the next planning cycle."),
        ("🎯", "Prioritize TikTok Search Campaigns",
         "A 712% ROI makes TikTok Search the highest-returning campaign type in the dataset. "
         "Expand keyword coverage and budget here as a near-term priority."),
        ("🛒", "Optimize Shopping Campaigns Across All Platforms",
         "Shopping campaigns consistently underperform Search. Review product feed quality, bidding "
         "strategies, and creative formats to close the performance gap."),
    ]

    for icon, title, detail in recs:
        with st.container(border=True):
            rc1, rc2 = st.columns([0.05, 0.95])
            with rc1:
                st.markdown(f"## {icon}")
            with rc2:
                st.markdown(f"**{title}**")
                st.markdown(detail)
