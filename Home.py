import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import matplotlib.ticker as mtick
import plotly.express as px

st.set_page_config(
    page_title="Platform Ad Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Data
@st.cache_data
def load_data():
    df = pd.read_csv('global_sales_data.csv')
    df.rename(columns={'platform': 'Platform'}, inplace=True)
    return df

df = load_data()
df_full = df.copy()  # always unfiltered — used for geo matrix, recs, campaign small multiples

# Sidebar
st.sidebar.header("Filters")
st.sidebar.caption("Filters apply to Sections 1–4. Market intelligence and recommendations always show full dataset.")

selected_country = st.sidebar.selectbox(
    "Country", options=["All"] + sorted(df['country'].dropna().unique())
)
selected_industry = st.sidebar.selectbox(
    "Industry", options=["All"] + sorted(df['industry'].dropna().unique())
)

df_f = df.copy()
if selected_industry != "All":
    df_f = df_f[df_f['industry'] == selected_industry]
if selected_country != "All":
    df_f = df_f[df_f['country'] == selected_country]

platforms = ['Google Ads', 'Meta Ads', 'TikTok Ads']
platform_palette = {
    "Google Ads": "#7FA6C9",
    "Meta Ads":   "#8FBF9F",
    "TikTok Ads": "#E39A8A"
}

#Pre-compute filtered aggregates
pf = df_f.groupby('Platform')[['ad_spend', 'revenue']].sum()
pf['ROI']          = ((pf['revenue'] - pf['ad_spend']) / pf['ad_spend'] * 100).round(1)
pf['Budget Share'] = (pf['ad_spend'] / pf['ad_spend'].sum() * 100).round(1)
pf['Median ROAS']  = df_f.groupby('Platform')['ROAS'].median().round(2)
pf['Median CPA']   = df_f.groupby('Platform')['CPA'].median().round(2)
pf['Avg CTR']      = (df_f.groupby('Platform')['CTR'].mean() * 100).round(2)

total_spend   = df_f['ad_spend'].sum()
total_revenue = df_f['revenue'].sum()
blended_roi   = (total_revenue - total_spend) / total_spend * 100

#Header
_, hcol, _ = st.columns([1, 3, 1])
with hcol:
    st.title("Platform Ad Intelligence")
    filter_label = []
    if selected_country  != "All": filter_label.append(selected_country)
    if selected_industry != "All": filter_label.append(selected_industry)
    st.caption(
        "Full dataset · 1,800 campaigns · 3 platforms · 7 countries · 5 industries" +
        (f"  ·  Filtered: {', '.join(filter_label)}" if filter_label else "")
    )
st.divider()

# SECTION 1 — HEADLINE KPIs  (filter-aware)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Spend",   f"${total_spend/1e6:.1f}M")
k2.metric("Total Revenue", f"${total_revenue/1e6:.1f}M")
k3.metric("Blended ROI",   f"{blended_roi:.0f}%")
k4.metric("Google ROAS",   f"{pf.loc['Google Ads',  'Median ROAS']:.2f}x")
k5.metric("Meta ROAS",     f"{pf.loc['Meta Ads',    'Median ROAS']:.2f}x")
k6.metric("TikTok ROAS",   f"{pf.loc['TikTok Ads',  'Median ROAS']:.2f}x")

st.divider()

# SECTION 2 — PLATFORM EFFICIENCY  (filter-aware)

st.markdown("### Platform Efficiency")

s2a, s2b, s2c = st.columns([1.1, 1.1, 0.9])

with s2a:
    roi_vals = pf['ROI'].reindex(platforms)
    fig_roi, ax_roi = plt.subplots(figsize=(5, 3.8))
    bars = ax_roi.bar(platforms, roi_vals,
                      color=[platform_palette[p] for p in platforms],
                      edgecolor='white', width=0.5)
    for bar, val in zip(bars, roi_vals):
        ax_roi.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                    f"{val:.0f}%", ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#333333')
    ax_roi.set_ylabel("ROI (%)", fontsize=9)
    ax_roi.set_title("Return on Ad Spend", fontsize=11, fontweight='bold', pad=8)
    ax_roi.spines[['top', 'right']].set_visible(False)
    ax_roi.grid(axis='y', color='#EEEEEE', linewidth=0.8)
    ax_roi.set_ylim(0, roi_vals.max() * 1.2)
    plt.setp(ax_roi.get_xticklabels(), fontsize=9)
    plt.tight_layout()
    st.pyplot(fig_roi)
    st.caption("(Revenue − Spend) / Spend. True return per dollar, not raw volume.")

with s2b:
    fig_cpa, ax_cpa = plt.subplots(figsize=(5, 3.8))
    sns.violinplot(data=df_f, x="CPA", y="Platform", palette=platform_palette,
                   order=platforms, inner="quartile", linewidth=1.1, ax=ax_cpa)
    ax_cpa.set_title("Cost Per Acquisition", fontsize=11, fontweight='bold', pad=8)
    ax_cpa.set_xlabel("CPA ($)", fontsize=9)
    ax_cpa.set_ylabel("")
    ax_cpa.spines[['top', 'right']].set_visible(False)
    ax_cpa.grid(axis='x', color='#EEEEEE', linewidth=0.8)
    ax_cpa.xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    plt.setp(ax_cpa.get_yticklabels(), fontsize=9)
    plt.tight_layout()
    st.pyplot(fig_cpa)
    st.caption("Inner lines: Q1, median, Q3. Width = density of campaign outcomes.")

with s2c:
    st.markdown("**Platform Summary**")
    tbl = pf[['Budget Share', 'ROI', 'Median ROAS', 'Median CPA', 'Avg CTR']].copy()
    tbl.index = tbl.index.map(lambda x: x.replace(' Ads', ''))
    tbl['Budget Share'] = tbl['Budget Share'].map(lambda x: f"{x}%")
    tbl['ROI']          = tbl['ROI'].map(lambda x: f"{x}%")
    tbl['Median ROAS']  = tbl['Median ROAS'].map(lambda x: f"{x}x")
    tbl['Median CPA']   = tbl['Median CPA'].map(lambda x: f"${x}")
    tbl['Avg CTR']      = tbl['Avg CTR'].map(lambda x: f"{x}%")
    st.dataframe(tbl, use_container_width=True)
    st.caption("⚠️ TikTok holds ~24% of budget but leads on every efficiency metric.")

st.divider()

# SECTION 3 — RETURN QUALITY & ENGAGEMENT  (filter-aware)

st.markdown("### Return Quality & Engagement")

s3a, s3b = st.columns(2)

with s3a:
    fig_box, ax_box = plt.subplots(figsize=(6, 4))
    roas_data = [df_f[df_f['Platform'] == p]['ROAS'].dropna().values for p in platforms]
    bp = ax_box.boxplot(roas_data, patch_artist=True, vert=True,
                        medianprops=dict(color='#333333', linewidth=2),
                        whiskerprops=dict(linewidth=1.2),
                        capprops=dict(linewidth=1.2),
                        flierprops=dict(marker='o', markersize=2, alpha=0.35))
    for patch, p in zip(bp['boxes'], platforms):
        patch.set_facecolor(platform_palette[p])
        patch.set_alpha(0.85)
    ax_box.set_xticks([1, 2, 3])
    ax_box.set_xticklabels(platforms, fontsize=10)
    ax_box.set_ylabel("ROAS", fontsize=10)
    ax_box.set_title("ROAS Distribution by Platform", fontsize=12, fontweight='bold', pad=10)
    ax_box.spines[['top', 'right']].set_visible(False)
    ax_box.grid(axis='y', color='#EEEEEE', linewidth=0.8)
    for i, p in enumerate(platforms):
        med = df_f[df_f['Platform'] == p]['ROAS'].median()
        ax_box.text(i + 1, med + 0.25, f"{med:.2f}x",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#333333')
    plt.tight_layout()
    st.pyplot(fig_box)
    st.caption("Box = IQR; whiskers = 1.5×IQR. Medians annotated.")

with s3b:
    ctr_vals = pf['Avg CTR'].reindex(platforms)
    fig_ctr, ax_ctr = plt.subplots(figsize=(6, 4))
    bars = ax_ctr.barh(platforms, ctr_vals,
                       color=[platform_palette[p] for p in platforms],
                       edgecolor='white', height=0.45)
    for bar, val in zip(bars, ctr_vals):
        ax_ctr.text(bar.get_width() + 0.04, bar.get_y() + bar.get_height() / 2,
                    f"{val:.2f}%", va='center', fontsize=11,
                    fontweight='bold', color='#333333')
    ax_ctr.set_xlabel("Average CTR (%)", fontsize=10)
    ax_ctr.set_title("Average Click-Through Rate by Platform", fontsize=12, fontweight='bold', pad=10)
    ax_ctr.spines[['top', 'right', 'left']].set_visible(False)
    ax_ctr.grid(axis='x', color='#EEEEEE', linewidth=0.8)
    ax_ctr.set_xlim(0, ctr_vals.max() * 1.28)
    plt.tight_layout()
    st.pyplot(fig_ctr)
    st.caption("CTR = Clicks / Impressions. Higher = stronger creative–audience fit.")

st.divider()

# SECTION 4 — CAMPAIGN TYPE SMALL MULTIPLES  (full dataset)

st.markdown("### Campaign Type Performance")
st.caption("Always shown on full dataset — campaign-type splits become unreliable on small filtered slices.")

ct = df_full.groupby(['Platform', 'campaign_type']).agg(
    total_spend=('ad_spend', 'sum'),
    total_revenue=('revenue', 'sum'),
    total_conversions=('conversions', 'sum'),
    total_impressions=('impressions', 'sum')
).reset_index()
ct['ROI'] = ((ct['total_revenue'] - ct['total_spend']) / ct['total_spend'] * 100).round(1)
campaign_types = sorted(ct['campaign_type'].unique())
median_roi = ct['ROI'].median()

fig_sm, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
for ax, platform in zip(axes, platforms):
    sub = ct[ct['Platform'] == platform].set_index('campaign_type').reindex(campaign_types)
    colors_ct = ['#6FAF8F' if v >= median_roi else '#D67A6A'
                 for v in sub['ROI'].fillna(0)]
    bars = ax.bar(campaign_types, sub['ROI'].fillna(0),
                  color=colors_ct, edgecolor='white', width=0.52)
    for bar, val in zip(bars, sub['ROI'].fillna(0)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"{val:.0f}%", ha='center', va='bottom',
                fontsize=8.5, fontweight='bold', color='#333333')
    ax.set_title(platform, fontsize=11, fontweight='bold', pad=8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color='#EEEEEE', linewidth=0.8)
    ax.set_ylim(0, ct['ROI'].max() * 1.22)
    ax.tick_params(axis='x', labelsize=9, rotation=15)
    if ax == axes[0]:
        ax.set_ylabel("ROI (%)", fontsize=10)

above_patch = mpatches.Patch(color='#6FAF8F', label=f'≥ median ROI ({median_roi:.0f}%)')
below_patch = mpatches.Patch(color='#D67A6A', label='< median ROI')
fig_sm.legend(handles=[above_patch, below_patch], loc='upper right', fontsize=9, frameon=False)
fig_sm.suptitle("ROI by Campaign Type — per Platform", fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
st.pyplot(fig_sm)
st.caption("TikTok Search (712% ROI) is the single best campaign–platform pair. Google Display (216%) is the weakest.")

st.divider()

# SECTION 5 — GEOGRAPHIC & INDUSTRY ROI MATRIX  (full dataset)

st.markdown("### Market Intelligence")
st.caption("Always shown on full dataset for complete geographic coverage.")

ci = df_full.groupby(['country', 'industry']).agg(
    total_spend=('ad_spend', 'sum'), total_revenue=('revenue', 'sum')
).reset_index()
ci['ROI'] = ((ci['total_revenue'] - ci['total_spend']) / ci['total_spend'] * 100).round(1)

s5a, s5b = st.columns([1.6, 1])

with s5a:
    heatmap_data = ci.pivot(index='country', columns='industry', values='ROI')
    fig_hm, ax_hm = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="RdYlGn",
                linewidths=0.5, linecolor='white', ax=ax_hm,
                cbar_kws={'label': 'ROI (%)', 'shrink': 0.8})
    ax_hm.set_title("ROI % by Country & Industry", fontsize=12, fontweight='bold', pad=10)
    ax_hm.set_xlabel("")
    ax_hm.set_ylabel("")
    plt.xticks(rotation=20, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    st.pyplot(fig_hm)

with s5b:
    st.markdown("**🟢 Top 5 Combinations**")
    top5 = ci.sort_values('ROI', ascending=False).head(5)[['country', 'industry', 'ROI']].copy()
    top5['ROI'] = top5['ROI'].map(lambda x: f"{x:.1f}%")
    st.dataframe(top5.reset_index(drop=True), use_container_width=True, hide_index=True)

    st.markdown("**🔴 Bottom 5 Combinations**")
    bot5 = ci.sort_values('ROI', ascending=True).head(5)[['country', 'industry', 'ROI']].copy()
    bot5['ROI'] = bot5['ROI'].map(lambda x: f"{x:.1f}%")
    st.dataframe(bot5.reset_index(drop=True), use_container_width=True, hide_index=True)

st.divider()

# SECTION 6 — SPEND DISTRIBUTION SUNBURST  (filter-aware)

st.markdown("### Spend Distribution by Market")

ci_f = df_f.groupby(["country", "industry"]).agg(
    total_spend=("ad_spend", "sum"), total_revenue=("revenue", "sum")
).reset_index()
ci_f['total_spend'] = ci_f['total_spend'].round(0)
ci_f["ROI"] = ((ci_f["total_revenue"] - ci_f["total_spend"]) / ci_f["total_spend"] * 100).round(1)

fig_sun = px.sunburst(
    ci_f, path=['country', 'industry'], values='total_spend',
    color='ROI', color_continuous_scale="RdYlGn",
    hover_data={'ROI': ':.1f', 'total_spend': ':,.0f'},
)
fig_sun.update_traces(textinfo="label+percent entry")
fig_sun.update_layout(
    title=dict(
        text="Ad Spend by Country → Industry  (color = ROI %)",
        x=0.5, xanchor='center', font_size=15
    ),
    height=580,
    margin=dict(t=50, l=0, r=0, b=0),
    coloraxis_colorbar=dict(title="ROI %")
)
st.plotly_chart(fig_sun, use_container_width=True)
st.caption("Segment size = total ad spend. Green = high ROI, red = low. Click a country ring to drill in.")

st.divider()

# SECTION 7 — STRATEGIC RECOMMENDATIONS  (full dataset, always)

st.markdown("### Strategic Recommendations")
st.caption("Based on full dataset analysis — not affected by sidebar filters.")

recs = [
    ("🔁", "Rebalance Budget Toward TikTok",
     "TikTok delivers 662% ROI with the lowest CPA ($22.22) yet holds only 24% of total spend. "
     "Shifting 15–20% of Google's budget to TikTok could improve blended returns."),
    ("🔍", "Audit Google Ads Display Campaigns",
     "At 216% ROI and a $48.24 median CPA, Google Display is the weakest investment in the portfolio. "
     "Pause or restructure in favour of Google Search (292% ROI) where intent-based targeting works."),
    ("📈", "Scale Canada E-commerce & India EdTech",
     "Both combinations exceeded 530% ROI. Increasing spend"
     "campaigns in these markets represents the clearest upside opportunity."),
    ("🇺🇸", "Investigate US Market Performance",
     "3 of the 5 US industry combinations rank in the bottom tier (254–274% ROI). A full creative, "
     "keyword, and competitive audit is recommended before the next planning cycle."),
    ("🎯", "Prioritise TikTok Search Campaigns",
     "712% ROI makes TikTok Search the highest-returning campaign type in the dataset. "
     "Expand budget allocation here as a priority."),
    ("🛒", "Optimise Shopping Campaigns Across All Platforms",
     "Shopping campaigns consistently underperforms compared to Search on every platform. Review product feed "
     "quality, and creative formats to close the performance gap."),
]

col_a, col_b = st.columns(2)
for i, (icon, title, detail) in enumerate(recs):
    col = col_a if i % 2 == 0 else col_b
    with col:
        with st.container(border=True):
            ic, tx = st.columns([0.08, 0.92])
            with ic:
                st.markdown(f"### {icon}")
            with tx:
                st.markdown(f"**{title}**")
                st.markdown(detail)
