import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import text
from src.database import get_engine
from src.ai_assistant import ask_business_question


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Sales Analytics Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# CUSTOM DARK THEME
# ==================================================

st.markdown("""
<style>

.stApp {
    background-color: #0B1420;
    color: #F1F5F9;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

header[data-testid="stHeader"] {
    background-color: #0B1420;
}

/* Hide every sidebar collapse / expand button */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="header"] {
    display: none !important;
}

/* Keep the sidebar permanently open, even if Streamlit marks it collapsed */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"][aria-expanded="false"],
section[data-testid="stSidebar"][aria-expanded="true"] {
    transform: none !important;
    visibility: visible !important;
    display: block !important;
    position: relative !important;
    margin-left: 0 !important;
    left: 0 !important;
    min-width: 375px !important;
    width: 375px !important;
    background-color: #101C2B;
    border-right: 1px solid #23364A;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

[data-testid="stMetric"] {
    background-color: #142232;
    border: 1px solid #23364A;
    padding: 22px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #AAB8C8;
}

[data-testid="stMetricValue"] {
    color: #F8FAFC;
}

[data-testid="stMetricDelta"] {
    color: #27D3C2;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #142232;
    border: 1px solid #23364A;
    border-radius: 12px;
}

h1, h2, h3 {
    color: #F8FAFC !important;
}

.stSelectbox label,
.stMultiSelect label,
.stDateInput label {
    color: #CBD5E1 !important;
}

div[data-baseweb="select"] > div {
    background-color: #142232;
    border-color: #23364A;
}

[data-testid="stDataFrame"] {
    border: 1px solid #23364A;
    border-radius: 10px;
}

/* AI Copilot chat messages */
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 12px !important;
    margin-bottom: 10px !important;
}

/* Chat message text */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {
    color: #111827 !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border-color: #d1d5db !important;
}

[data-testid="stChatInput"] textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    caret-color: #111827 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #6b7280 !important;
}

/* Code and links inside chat */
[data-testid="stChatMessage"] pre,
[data-testid="stChatMessage"] code {
    background-color: #f3f4f6 !important;
    color: #111827 !important;
}

[data-testid="stChatMessage"] a {
    color: #2563eb !important;
}

.stButton > button {
    border-radius: 9px;
    border: 1px solid #34465B;
    background-color: #18283A;
    color: #F1F5F9;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #20B8D2;
    color: #20B8D2;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ==================================================
# AI COPILOT - LEFT SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown(
        """
        <div style="font-size:25px; font-weight:700; color:#F8FAFC;">
            🤖 Sales Copilot
        </div>
        <div style="font-size:12px; color:#94A3B8; margin-top:5px;">
            Your intelligent business analyst
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # New conversation button
    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    # Suggested questions
    st.markdown("### Suggested questions")

    suggestions = [
        "What are our total sales and profit?",
        "Which category performs best?",
        "Which region generates the most sales?",
        "Which products are generating losses?",
        "What are our top 10 products?",
        "How can we improve business performance?"
    ]

    for index, suggestion in enumerate(suggestions):

        if st.button(
            suggestion,
            key=f"suggestion_{index}",
            use_container_width=True
        ):
            st.session_state.pending_question = suggestion
            st.rerun()

    st.divider()

    st.markdown("### Conversation")

    # Display chat history
    chat_container = st.container(height=430)

    with chat_container:

        if not st.session_state.messages:

            st.markdown(
                """
                <div style="
                    text-align:center;
                    padding:30px 5px;
                    color:#94A3B8;
                ">
                    <div style="font-size:35px;">💬</div>
                    <b>Welcome to Sales Copilot</b>
                    <p style="font-size:12px;">
                        Ask questions about your sales,
                        products, profit and business performance.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        for message in st.session_state.messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    question = st.chat_input(
        "Ask your business question...",
        key="sales_copilot_chat"
    )

    # Handle suggested questions
    if st.session_state.pending_question:

        question = st.session_state.pending_question
        st.session_state.pending_question = None

    # Process user question
    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with chat_container:

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):

                with st.spinner("Analyzing business data..."):

                    try:

                        answer = ask_business_question(question)

                        st.markdown(answer)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })

                    except Exception as error:

                        error_message = (
                            f"Sorry, I couldn't process your question.\n\n"
                            f"Error: {type(error).__name__}: {error}"
                        )

                        st.error(error_message)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_message
                        })


# ==================================================
# LOAD POSTGRESQL DATA
# ==================================================

@st.cache_data(ttl=300)
def load_data():

    engine = get_engine()

    query = "SELECT * FROM superstore"

    with engine.connect() as connection:

        data = pd.read_sql_query(
            text(query),
            connection
        )

    data.columns = data.columns.str.lower()

    data["order_date"] = pd.to_datetime(
        data["order_date"],
        errors="coerce"
    )

    data["sales"] = pd.to_numeric(
        data["sales"],
        errors="coerce"
    )

    data["profit"] = pd.to_numeric(
        data["profit"],
        errors="coerce"
    )

    data["quantity"] = pd.to_numeric(
        data["quantity"],
        errors="coerce"
    )

    return data.dropna(
        subset=["order_date", "sales", "profit"]
    )


try:

    df = load_data()

except Exception as error:

    st.error(f"Database connection failed: {error}")
    st.stop()


if df.empty:

    st.warning("No sales data available.")
    st.stop()


# ==================================================
# MAIN DASHBOARD HEADER
# ==================================================

st.title("📊 Sales Overview")

st.caption(
    "AI-Powered Sales Analytics Copilot | "
    "Business Intelligence Dashboard"
)


# ==================================================
# TOP FILTERS
# ==================================================

f1, f2, f3 = st.columns(3)

regions = sorted(
    df["region"].dropna().unique()
)

categories = sorted(
    df["category"].dropna().unique()
)

years = sorted(
    df["order_date"].dt.year.dropna().unique()
)

with f1:

    selected_region = st.selectbox(
        "Region",
        ["All Regions"] + regions
    )

with f2:

    selected_category = st.selectbox(
        "Category",
        ["All Categories"] + categories
    )

with f3:

    selected_year = st.selectbox(
        "Year",
        ["All Years"] + years
    )


# ==================================================
# FILTER DATA
# ==================================================

filtered_df = df.copy()

if selected_region != "All Regions":

    filtered_df = filtered_df[
        filtered_df["region"] == selected_region
    ]

if selected_category != "All Categories":

    filtered_df = filtered_df[
        filtered_df["category"] == selected_category
    ]

if selected_year != "All Years":

    filtered_df = filtered_df[
        filtered_df["order_date"].dt.year == selected_year
    ]


if filtered_df.empty:

    st.warning("No records found for these filters.")
    st.stop()


# ==================================================
# KPI CALCULATIONS
# ==================================================

total_sales = filtered_df["sales"].sum()

total_profit = filtered_df["profit"].sum()

total_orders = filtered_df["order_id"].nunique()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales else 0
)


# ==================================================
# YEAR-OVER-YEAR REVENUE GROWTH
# ==================================================

yearly_sales = (
    df.groupby(df["order_date"].dt.year)["sales"]
    .sum()
    .sort_index()
)

if selected_year != "All Years":

    comparison_year = selected_year

else:

    comparison_year = yearly_sales.index.max()


previous_year = comparison_year - 1

if previous_year in yearly_sales.index:

    previous_sales = yearly_sales.loc[previous_year]

    current_sales = yearly_sales.loc[comparison_year]

    growth = (
        (current_sales - previous_sales) / previous_sales * 100
        if previous_sales else 0
    )

else:

    growth = None


# ==================================================
# KPI CARDS
# ==================================================

st.markdown("### Business Performance")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Revenue",
    f"${total_sales:,.0f}",
    help="Total sales revenue for the selected filters."
)

c2.metric(
    "Total Profit",
    f"${total_profit:,.0f}",
    help="Total profit for the selected filters."
)

c3.metric(
    "Revenue Growth",
    f"{growth:+.2f}%" if growth is not None else "N/A",
    help="Year-over-year revenue growth. Uses the full dataset."
)

st.caption(
    f"Orders: {total_orders:,} | "
    f"Profit Margin: {profit_margin:.2f}%"
)

st.divider()


# ==================================================
# MONTHLY SALES TREND
# ==================================================

left, right = st.columns([1.6, 1])

with left:

    st.subheader("Sales Trend")

    monthly_sales = (
        filtered_df
        .assign(
            month=filtered_df["order_date"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )
        .groupby("month", as_index=False)["sales"]
        .sum()
        .sort_values("month")
    )

    fig_monthly = px.line(
        monthly_sales,
        x="month",
        y="sales",
        markers=True,
        template="plotly_dark"
    )

    fig_monthly.update_traces(
        line=dict(
            color="#20B8D2",
            width=3
        ),
        fill="tozeroy",
        fillcolor="rgba(32,184,210,0.10)"
    )

    fig_monthly.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=15, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title=None,
        yaxis_title="Revenue",
        showlegend=False
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )


# ==================================================
# SALES BY SEGMENT
# ==================================================

with right:

    st.subheader("Sales by Segment")

    if "segment" in filtered_df.columns:

        segment_sales = (
            filtered_df.groupby(
                "segment",
                as_index=False
            )["sales"]
            .sum()
            .sort_values(
                "sales",
                ascending=False
            )
        )

        fig_segment = px.bar(
            segment_sales,
            x="segment",
            y="sales",
            color="segment",
            template="plotly_dark"
        )

        fig_segment.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=15, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False
        )

        st.plotly_chart(
            fig_segment,
            use_container_width=True
        )


st.divider()


# ==================================================
# CATEGORY ANALYSIS
# ==================================================

left, right = st.columns([1, 1.4])

with left:

    st.subheader("Sales by Category")

    category_sales = (
        filtered_df.groupby(
            "category",
            as_index=False
        )["sales"]
        .sum()
        .sort_values(
            "sales",
            ascending=False
        )
    )

    fig_category = px.pie(
        category_sales,
        names="category",
        values="sales",
        hole=0.65,
        template="plotly_dark"
    )

    fig_category.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ==================================================
# TOP PRODUCTS
# ==================================================

with right:

    st.subheader("Top Products")

    top_products = (
        filtered_df.groupby(
            "product_name",
            as_index=False
        )
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum")
        )
        .sort_values(
            "sales",
            ascending=False
        )
        .head(10)
    )

    top_products["sales"] = (
        top_products["sales"].round(2)
    )

    top_products["profit"] = (
        top_products["profit"].round(2)
    )

    st.dataframe(
        top_products,
        use_container_width=True,
        hide_index=True,
        height=350
    )


# ==================================================
# PRODUCT PERFORMANCE TABLE
# ==================================================

st.divider()

st.subheader("Product Performance")

product_summary = (
    filtered_df.groupby(
        "product_name",
        as_index=False
    )
    .agg(
        sales=("sales", "sum"),
        profit=("profit", "sum")
    )
)

product_summary["cost"] = (
    product_summary["sales"] -
    product_summary["profit"]
)

product_summary = product_summary.sort_values(
    "sales",
    ascending=False
).head(20)

product_summary = product_summary.rename(
    columns={
        "product_name": "Product",
        "sales": "Sales",
        "cost": "Estimated Cost",
        "profit": "Profit"
    }
)

st.dataframe(
    product_summary.style.format({
        "Sales": "${:,.2f}",
        "Estimated Cost": "${:,.2f}",
        "Profit": "${:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "AI-Powered Sales Analytics Copilot | "
    "Python • PostgreSQL • Streamlit • Plotly • Gemini AI"
)