import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Page Config ----
st.set_page_config(page_title="Monthly Products", layout="wide")

# ---- Load & Clean Data ----
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    # اقرأ بـ ; لأن بياناتك مفصولة بسيمي كولون
    df = pd.read_csv(path, sep=';', encoding="utf-8-sig")

    # نظّف أسماء الأعمدة
    df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=True)

    # نظافة أعمدة نصية
    df["Product"] = df["Product"].astype(str).str.strip()
    df["Branch"]  = df["Branch"].astype(str).str.strip()

    # تحويل رقمي
    df["Sales"]    = pd.to_numeric(df["Sales"], errors="coerce").fillna(0)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
    df["Visitors"] = pd.to_numeric(df["Visitors"], errors="coerce").fillna(0)

    # تحويل التاريخ بصيغة بياناتك: DD/MM/YY (مثال: 01/08/25)
    df["Month"] = df["Month"].astype(str).str.strip()
    df["Month"] = pd.to_datetime(df["Month"], format="%d/%m/%y", errors="coerce")

    # أنشئ عمود Month_Name (هنا كان النقص)
    df["Month_Name"] = df["Month"].dt.strftime("%B %Y")

    # حماية: لو فشل التحويل لأي صف، أعطِ تنبيه بدل ما ينهار البرنامج
    if df["Month"].isna().any():
        st.warning("⚠️ بعض الصفوف لم يتمكن pandas من تحويلها لتاريخ. تأكد أن الصيغة مثل 01/08/25 (DD/MM/YY).")

    return df

# ---- Load Data ----
df_full = load_data("Products_2025.csv")

# ---- Title with Logo ----
col1, col2 = st.columns([7, 1]) 
with col1:
    st.markdown(
        """
        <h1 style="color:#2E86C1; font-size:36px; margin-top:15px;">
            📊 Monthly Products Dashboard
        </h1>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.image(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcThAsJgb1nN-XLqXMsXh6DYAE-qTUf1lEG2tw&s",
        width=120
    )

# ---- Tabs ----
tab1, tab2 = st.tabs(["🌍 Overview", "📦 Product"])

st.markdown("""
    <style>
        .metric-card {
            margin-top: 5px !important;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            text-align: center;
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .metric-card h4 {
            font-size: 16px;
            color: #666;
            margin-bottom: 6px;
        }
        .metric-card h2 {
            font-size: 28px;
            margin: 0;
            color: #222;
        }
        .metric-card p {
            font-size: 13px;
            margin-top: 4px;
        }
        .positive { color: green; }
        .negative { color: red; }
        .neutral { color: gray; }
        .main-container {
            max-width: 90%;
            margin: auto;
        }
        [data-testid="stPlotlyChart"] > div {
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            padding: 10px;
            margin: 10px 0;
            overflow: hidden;
        }
                
        [data-testid="stSelectbox"] {
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        padding: 10px;
        margin: 10px 0;
        }
        
        [data-testid="stSelectbox"] {
            margin-bottom: 2px !important;  
        }
        
        [data-testid="stPlotlyChart"] > div,
            .stPlotlyChart > div,
            .plot-card {
            background: #fff !important;
            border-radius: 15px !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
            padding: 10px !important;
            margin: 10px 0 !important;            
            overflow: hidden !important;
            max-width: 98.4% !important;      
        }

        .plot-card .js-plotly-plot,
        .stPlotlyChart .js-plotly-plot {
        border-radius: 15px !important;
        } 
         </style>
    """, unsafe_allow_html=True)

with tab1:

    df = df_full.copy()

    # ---- Month Filter ----
    months = sorted(df["Month_Name"].dropna().unique())
    if months:
        selected_month = st.selectbox("📅 Select Month", months, index=len(months)-1)
        df = df[df["Month_Name"] == selected_month]
    else:
        st.warning("⚠️ No valid month data found in the file.")
        st.stop()

    # ---- KPIs ----
    unique_products = df["Product"].nunique()
    unique_visitors_sum = df["Visitors"].drop_duplicates().sum()  # ✅ جمع القيم الفريدة فقط
    total_quantity = df["Quantity"].sum()
    total_sales = df["Sales"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Products Types (This Month)</h4>
                <h2>{unique_products:,}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>👥 Visitors</h4>
                <h2>{unique_visitors_sum:,.0f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>📦 Total Quantity</h4>
                <h2>{total_quantity:,.0f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>💰 Total Sales (SAR)</h4>
                <h2>{total_sales:,.0f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

    # ---- Products with Zero Sales (Across All Branches) ----
    st.subheader("❌ Products with Zero Sales Across All Branches")

    # نحسب مجموع المبيعات لكل منتج عبر جميع الفروع
    zero_sales_all = (
        df.groupby("Product", as_index=False)["Sales"].sum()
        .query("Sales == 0")  # المنتجات التي مجموع مبيعاتها صفر
    )

    if zero_sales_all.empty:
        st.success("🎉 No products with zero sales in any branch this month!")
    else:
        st.dataframe(zero_sales_all, use_container_width=True)

    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

    # ---- Branch Summary for Selected Month ----
    st.subheader("🏬 Branch Performance (Unique Visitors & Total Quantity)")

    # نحسب إجمالي الكمية لكل فرع
    # وعدد الزوار بشكل فريد (كل رقم زوار يُحسب مرة واحدة فقط)
    branch_summary = (
        df.groupby("Branch", as_index=False)
        .agg({
            "Sales": "sum",
            "Quantity": "sum",
            "Visitors": lambda x: x.drop_duplicates().sum()
        })
        .sort_values("Quantity", ascending=False)  # ترتيب تنازلي حسب الكمية
    )

    # عرض النتائج
    st.dataframe(branch_summary, use_container_width=True)

    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

    # ---- Total Quantity per Product (Across All Branches) ----
    st.subheader("📦 Total Quantity per Product (All Branches Combined)")

    # نجمع الكميات لكل منتج بغض النظر عن الفروع
    product_quantity = (
        df.groupby("Product", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=False)
    )

    # نعرض النتيجة في جدول
    st.dataframe(product_quantity, use_container_width=True)

    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

    # ---- Purchase Rate per Product ----
    # حساب إجمالي الزوار الفريدين في الشهر المحدد (مرة واحدة)
    unique_visitors_total = df["Visitors"].drop_duplicates().sum()

    # مجموع الكمية لكل منتج (عبر جميع الفروع)
    product_summary = (
        df.groupby("Product", as_index=False)["Quantity"]
        .sum()
        .rename(columns={"Quantity": "Total_Quantity"})
    )

    # إضافة عمود الزوار (نفس القيمة للجميع لأنها إجمالي الزوار الفريدين في الشهر)
    product_summary["Unique_Visitors"] = unique_visitors_total

    # حساب النسبة المئوية للشراء
    product_summary["Purchase%"] = (
        (product_summary["Total_Quantity"] / product_summary["Unique_Visitors"]) * 100
    ).round(2)

    # ترتيب تنازلي حسب النسبة
    product_summary = product_summary.sort_values("Purchase%", ascending=False)

    # ---- تصنيف المنتجات حسب النسبة ----
    st.subheader("📊 Percentage of visitors out of the total number who purchased the product in all branches")

    cat1 = product_summary[product_summary["Purchase%"] >= 20].sort_values(by="Purchase%", ascending=False)
    cat2 = product_summary[(product_summary["Purchase%"] >= 15) & (product_summary["Purchase%"] < 20)].sort_values(by="Purchase%", ascending=False)
    cat3 = product_summary[(product_summary["Purchase%"] >= 10) & (product_summary["Purchase%"] < 15)].sort_values(by="Purchase%", ascending=False)
    cat4 = product_summary[product_summary["Purchase%"] < 10].sort_values(by="Purchase%", ascending=False)

    # الفئة 1️⃣ — أعلى من أو تساوي 20%
    st.markdown("**20% or higher**")
    if cat1.empty:
        st.warning("⚠️ No products achieved 20% or higher purchase rate this month.")
    else:
        st.dataframe(cat1, use_container_width=True)

    # الفئة 2️⃣ — بين 15% و 20%
    st.markdown("**15% and less than 20%**")
    if cat2.empty:
        st.warning("⚠️ No products achieved purchase rate between 15% and 20%.")
    else:
        st.dataframe(cat2, use_container_width=True)

    # الفئة 3️⃣ — بين 10% و 15%
    st.markdown("**10% and less than 15%**")
    if cat3.empty:
        st.warning("⚠️ No products achieved purchase rate between 10% and 15%.")
    else:
        st.dataframe(cat3, use_container_width=True)

    # الفئة 4️⃣ — أقل من 10%
    st.markdown("**Less than 10%**")
    if cat4.empty:
        st.warning("⚠️ No products below 10% purchase rate this month.")
    else:
        st.dataframe(cat4, use_container_width=True)

    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

    # ---- Branch Average Quantity per Visitor ----
    st.subheader("🏪 Average Number of Products per Visitor per Branch")

    # نحسب إجمالي الكمية وعدد الزوار الفريدين لكل فرع
    branch_summary_avg = (
        df.groupby("Branch", as_index=False)
        .agg({
            "Quantity": "sum",
            "Visitors": lambda x: x.drop_duplicates().sum()
        })
        .rename(columns={
            "Quantity": "Total_Quantity",
            "Visitors": "Unique_Visitors"
        })
    )

    # نحسب معدل المنتجات لكل زائر
    branch_summary_avg["Avg_Products_per_Visitor"] = (
        branch_summary_avg["Total_Quantity"] / branch_summary_avg["Unique_Visitors"]
    ).round(2)

    # نرتب من الأعلى إلى الأدنى حسب المعدل
    branch_summary_avg = branch_summary_avg.sort_values("Avg_Products_per_Visitor", ascending=False)

    # عرض النتائج في جدول
    st.dataframe(branch_summary_avg, use_container_width=True)

    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

with tab2:

    df_product = df_full.copy()
    
    st.subheader("Product performance in the same month across branches")

    # --- فلاتر في صف واحد ---
    col1, col2 = st.columns(2)

    with col1:
        product_list = sorted(df_product["Product"].unique())
        selected_product2 = st.selectbox("🎯 Select Product", product_list, key="prod_by_branch")

    with col2:
        month_list = sorted(df_product["Month_Name"].dropna().unique())
        selected_month2 = st.selectbox("📅 Select Month", month_list, key="month_by_branch")

    # --- تصفية البيانات بناءً على المنتج والشهر ---
    filtered_branch_df = df_product[
        (df_product["Product"] == selected_product2)
        & (df_product["Month_Name"] == selected_month2)
    ]

    # --- تحقق من البيانات ---
    if filtered_branch_df.empty:
        st.warning("⚠️ No data found for this product in the selected month.")
    else:
        # نحسب الكمية الإجمالية لكل فرع في ذلك الشهر
        branch_performance = (
            filtered_branch_df.groupby("Branch", as_index=False)["Quantity"]
            .sum()
            .sort_values("Quantity", ascending=False)
        )

        # --- حساب الإجمالي ---
        total_qty = branch_performance["Quantity"].sum()

        # --- رسم مخطط الأعمدة مع إضافة الإجمالي في العنوان ---
        fig_bar = px.bar(
            branch_performance,
            x="Branch",
            y="Quantity",
            text="Quantity",
            title=f"🏆 {selected_product2} — Quantity per Branch ({selected_month2}) | Total = {total_qty:,}",
            color="Quantity",
            color_continuous_scale="Blues"
        )

        fig_bar.update_traces(textposition="inside")
        fig_bar.update_layout(
            xaxis_title="Branch",
            yaxis_title="Quantity Sold",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=14)
        )

        st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

    st.subheader("Product performance in the same branch over months")    

        # ---- الفلاتر  ----
    col1, col2 = st.columns(2)

    with col1:
        product_list = sorted(df_product["Product"].unique())
        selected_product = st.selectbox("🎯 Select Product", product_list)

    with col2:
        branch_list = sorted(df_product["Branch"].unique())
        selected_branch = st.selectbox("🏬 Select Branch", branch_list)


    # ---- تصفية حسب المنتج والفرع ----
    filtered_df = df_product[
        (df_product["Product"] == selected_product) &
        (df_product["Branch"] == selected_branch)
    ]

    # ---- تحقق من وجود بيانات ----
    if filtered_df.empty:
        st.warning("⚠️ No data available for this product and branch.")
    else:
        # إجمالي الكمية حسب الشهر (لكل الشهور المتاحة)
        performance_df = (
            filtered_df.groupby("Month", as_index=False)["Quantity"]
            .sum()
            .sort_values("Month")
        )
        performance_df["Month_Name"] = performance_df["Month"].dt.strftime("%B %Y")

        # ---- حساب الإجمالي ----
        total_qty_line = performance_df["Quantity"].sum()

        # ---- رسم المخطط ----
        fig_line = px.line(
            performance_df,
            x="Month_Name",
            y="Quantity",
            text="Quantity",
            title=f"📈 {selected_product} — Quantity Trend per Month ({selected_branch}) | Total = {total_qty_line:,}",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#2E86C1"]
        )

        fig_line.update_traces(textposition="top center")
        fig_line.update_layout(
            xaxis_title="Month",
            yaxis_title="Quantity Sold",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=14)
        )

        st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("<hr style='border:2px solid #007BFF'>", unsafe_allow_html=True)

    # ---- Product Popularity per Branch & Month ----
    st.subheader("💫 Product Popularity by Branch and Month")

    # استخدم نسخة مستقلة من البيانات
    df_pop = df_full.copy()

    # --- فلاتر الشهر والفرع ---
    col1, col2 = st.columns(2)

    with col1:
        month_list = sorted(df_pop["Month_Name"].dropna().unique())
        selected_month_pop = st.selectbox(
            "📅 Select Month", 
            month_list, 
            key="popularity_month"
        )

    with col2:
        branch_list = sorted(df_pop["Branch"].dropna().unique())
        selected_branch_pop = st.selectbox(
            "🏬 Select Branch", 
            branch_list, 
            key="popularity_branch"
        )

    # --- تصفية البيانات ---
    filtered_pop = df_pop[
        (df_pop["Month_Name"] == selected_month_pop) &
        (df_pop["Branch"] == selected_branch_pop)
    ]

    if filtered_pop.empty:
        st.warning("⚠️ No data found for this branch in the selected month.")
    else:
        # عدد الزوار الفريدين للفرع في هذا الشهر
        unique_visitors = filtered_pop["Visitors"].drop_duplicates().sum()

        # حساب كمية المبيعات لكل منتج
        product_popularity = (
            filtered_pop.groupby("Product", as_index=False)["Quantity"]
            .sum()
            .rename(columns={"Quantity": "Total_Quantity"})
        )

        # حساب الشعبية
        product_popularity["Unique_Visitors"] = unique_visitors
        product_popularity["Popularity%"] = (
            (product_popularity["Total_Quantity"] / unique_visitors) * 100
        ).round(2)

        # ترتيب تنازلي حسب الشعبية
        product_popularity = product_popularity.sort_values("Popularity%", ascending=False)

        # عرض النتائج
        st.dataframe(product_popularity, use_container_width=True)
