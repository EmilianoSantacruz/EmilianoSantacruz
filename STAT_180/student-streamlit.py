import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Tips Dashboard",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Restaurant Tips Dashboard")
st.markdown("Explore restaurant bills and tips. Use filters to see patterns.")

# ===== LOAD DATA =====
df = sns.load_dataset("tips")

# Create useful columns
df = df.copy()
df["tip_pct"] = (df["tip"] / df["total_bill"]) * 100

# ===== SIDEBAR FILTERS =====
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

# ===== APPLY FILTERS =====
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

# Avoid divide by zero issues if user filters everything out
if len(filtered_df) == 0:
    st.warning("No rows match your filters. Try widening the filters.")
    st.stop()

# ===== KEY METRICS =====
st.subheader("Key Metrics")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Bills", len(filtered_df))

with c2:
    avg_tip_pct = filtered_df["tip_pct"].mean()
    st.metric("Average Tip %", f"{avg_tip_pct:.1f}%")

with c3:
    avg_bill = filtered_df["total_bill"].mean()
    st.metric("Average Bill", f"${avg_bill:.2f}")

with c4:
    max_bill = filtered_df["total_bill"].max()
    st.metric("Largest Bill", f"${max_bill:.2f}")

# ===== COLUMS =====
col1, col2, col3 = st.columns(["📊 Data", "📈 Visualizations", "ℹ️ Details"])

# col 1: DATA TABLE
with col1:
    st.subheader("Dataset")
    st.write(f"Showing {len(filtered_df)} of {len(df)} rows")
    st.dataframe(filtered_df, use_container_width=True)

# col 2: VISUALIZATIONS
with col2:
    st.subheader("Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Average Tip % by Day**")
        fig, ax = plt.subplots(figsize=(6, 4))
        tip_by_day = filtered_df.groupby("day")["tip_pct"].mean().reindex(sorted(df["day"].unique()))
        tip_by_day.plot(kind="bar", ax=ax)
        ax.set_xlabel("Day")
        ax.set_ylabel("Average Tip %")
        plt.xticks(rotation=0)
        st.pyplot(fig)

    with col2:
        st.write("**Total Bill Distribution**")
        fig, ax = plt.subplots(figsize=(6, 4))
        filtered_df["total_bill"].hist(bins=20, ax=ax, edgecolor="black")
        ax.set_xlabel("Total bill ($)")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    st.write("**Total Bill vs Tip (colored by meal time)**")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.scatterplot(data=filtered_df, x="total_bill", y="tip", hue="time", ax=ax)
    ax.set_xlabel("Total bill ($)")
    ax.set_ylabel("Tip ($)")
    st.pyplot(fig)

    st.write("**Tip % by Smoker**")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(data=filtered_df, x="smoker", y="tip_pct", ax=ax)
    ax.set_xlabel("Smoker")
    ax.set_ylabel("Tip %")
    st.pyplot(fig)

# col 3: DETAILS
with col3:
    st.subheader("Additional Information")

    with st.expander("📊 View Data Statistics"):
        st.write("**Descriptive statistics (numeric columns):**")
        st.dataframe(filtered_df[["total_bill", "tip", "size", "tip_pct"]].describe())

    with st.expander("🔗 View Correlation Matrix"):
        numeric_cols = ["total_bill", "tip", "size", "tip_pct"]
        corr = filtered_df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    with st.expander("📖 About This Dataset"):
        st.write("""
        **Tips Dataset (Seaborn)**
        
        This dataset includes restaurant bills and tips.
        
        **Main columns:**
        - **total_bill**: total bill in dollars
        - **tip**: tip in dollars
        - **sex**: sex of the person paying
        - **smoker**: Yes/No
        - **day**: day of the week
        - **time**: Lunch or Dinner
        - **size**: party size
        - **tip_pct**: tip percentage (tip / total_bill * 100)
        """)
