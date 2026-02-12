import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Restaurant Tips Dashboard",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Restaurant Tips Dashboard")
st.caption("Explore restaurant bills and tips. Use the sidebar filters to narrow results.")

df = sns.load_dataset("tips").copy()
df["tip_pct"] = (df["tip"] / df["total_bill"]) * 100

with st.sidebar:
    st.header("Filters")

    selected_days = st.multiselect(
        "Day:",
        options=sorted(df["day"].unique()),
        default=sorted(df["day"].unique())
    )

    selected_time = st.selectbox(
        "Meal time:",
        options=["All"] + sorted(df["time"].unique().tolist()),
        index=0
    )

    smoker_option = st.radio(
        "Smoker:",
        options=["All", "Yes", "No"],
        index=0
    )

    size_min, size_max = st.slider(
        "Party size range:",
        min_value=int(df["size"].min()),
        max_value=int(df["size"].max()),
        value=(int(df["size"].min()), int(df["size"].max()))
    )

    min_bill = st.number_input(
        "Minimum total bill ($):",
        min_value=0.0,
        max_value=float(df["total_bill"].max()),
        value=0.0,
        step=1.0
    )

filtered_df = df[
    (df["day"].isin(selected_days)) &
    (df["size"] >= size_min) &
    (df["size"] <= size_max) &
    (df["total_bill"] >= min_bill)
]

if selected_time != "All":
    filtered_df = filtered_df[filtered_df["time"] == selected_time]

if smoker_option != "All":
    filtered_df = filtered_df[filtered_df["smoker"] == smoker_option]

if len(filtered_df) == 0:
    st.warning("No rows match your filters. Try widening the filters.")
    st.stop()

tab_overview, tab_explore, tab_insights = st.tabs(["✅ Overview", "📊 Explore Data", "📈 Insights"])

with tab_overview:
    st.subheader("Key Metrics")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Rows", len(filtered_df))

    with c2:
        st.metric("Avg Tip %", f"{filtered_df['tip_pct'].mean():.1f}%")

    with c3:
        st.metric("Avg Bill", f"${filtered_df['total_bill'].mean():.2f}")

    with c4:
        st.metric("Avg Tip", f"${filtered_df['tip'].mean():.2f}")

    with c5:
        st.metric("Largest Bill", f"${filtered_df['total_bill'].max():.2f}")

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.write("**Average Tip % by Day**")
        fig, ax = plt.subplots(figsize=(6, 4))
        order_days = sorted(df["day"].unique())
        tip_by_day = filtered_df.groupby("day")["tip_pct"].mean().reindex(order_days)
        tip_by_day.plot(kind="bar", ax=ax)
        ax.set_xlabel("Day")
        ax.set_ylabel("Average Tip %")
        plt.xticks(rotation=0)
        st.pyplot(fig)

    with right:
        st.write("**Total Bill Distribution**")
        fig, ax = plt.subplots(figsize=(6, 4))
        filtered_df["total_bill"].hist(bins=20, ax=ax, edgecolor="black")
        ax.set_xlabel("Total bill ($)")
        ax.set_ylabel("Count")
        st.pyplot(fig)

with tab_explore:
    st.subheader("Filtered Dataset")
    st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** rows")
    st.dataframe(filtered_df, use_container_width=True)

    st.download_button(
        label="Download filtered data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="tips_filtered.csv",
        mime="text/csv"
    )

with tab_insights:
    st.subheader("Visual Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Total Bill vs Tip (by meal time)**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(data=filtered_df, x="total_bill", y="tip", hue="time", ax=ax)
        ax.set_xlabel("Total bill ($)")
        ax.set_ylabel("Tip ($)")
        st.pyplot(fig)

    with col2:
        st.write("**Tip % by Smoker**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=filtered_df, x="smoker", y="tip_pct", ax=ax)
        ax.set_xlabel("Smoker")
        ax.set_ylabel("Tip %")
        st.pyplot(fig)

    st.markdown("---")

    with st.expander("📊 Statistics"):
        st.dataframe(filtered_df[["total_bill", "tip", "size", "tip_pct"]].describe())

    with st.expander("🔗 Correlation Matrix"):
        numeric_cols = ["total_bill", "tip", "size", "tip_pct"]
        corr = filtered_df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    with st.expander("📖 About this dataset"):
        st.write("""
        **Tips Dataset (Seaborn)**

        This dataset includes restaurant bills and tips.

        **Columns:**
        - **total_bill**: total bill in dollars
        - **tip**: tip in dollars
        - **sex**: sex of the person paying
        - **smoker**: Yes/No
        - **day**: day of the week
        - **time**: Lunch or Dinner
        - **size**: party size
        - **tip_pct**: tip percentage (tip / total_bill * 100)
        """)
