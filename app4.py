import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_excel("raw_data.xlsx")
region_map = df[["Location_Region", "Selling_Location", "Area_Name"]].drop_duplicates()


# Page Title

st.set_page_config(page_title="AA Autoparts - What-If Margin Calculator", layout="wide")

st.title("🧮 AA - What-If Margin Calculator for Salespersons")
st.markdown("""
This simple tool helps sales associates understand **how discounts affect profitability** before finalizing a price.
""")


# Region–Location–Area linkage setup

regions = sorted(region_map["Location_Region"].dropna().unique())
region = st.selectbox("🌎 Location Region", ["(Select Region)"] + regions)

if region != "(Select Region)":
    filtered_df = region_map[region_map["Location_Region"] == region]
    selling_locations = sorted(filtered_df["Selling_Location"].dropna().unique())
    area_names = sorted(filtered_df["Area_Name"].dropna().unique())
else:
    selling_locations = sorted(region_map["Selling_Location"].dropna().unique())
    area_names = sorted(region_map["Area_Name"].dropna().unique())


# Three-Column Input Layout

col1, col2, col3 = st.columns(3)

# -------- Column 1: Product & Region --------
with col1:
    product_ids = sorted(df["product_id"].dropna().unique())
    product_id = st.selectbox("🧾 Product ID", product_ids)

    part_categories = sorted(df["Part_Category"].dropna().unique())
    part_category = st.selectbox("🧩 Part Category", part_categories)

    location_region = region  
    st.text_input("🌍 Location Region", value=location_region, disabled=True)

# -------- Column 2: Selling Info --------
with col2:
    selling_location = st.selectbox("🏪 Selling Location", selling_locations)
    area_name = st.selectbox("📍 Area Name", area_names)
    base_price = st.number_input("Base Price ($)", min_value=0.0, value=900.0, step=10.0)

# -------- Column 3: Financial Levers --------
with col3:
    selling_cost = st.number_input("Selling Cost ($)", min_value=0.0, value=620.0, step=10.0)
    discount_pct = st.slider("Discount %", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)


# Region-based margin modifiers (based on EDA, values obtained by dividing the avg gross margin% by the overall mean: further can be discussed with the business)

REGION_MODIFIER = {
    'WEST': 0.93,      
    'CENTRAL': 0.99,   
    'NORTHEAST': 1.10,
    'SOUTHEAST': 0.98 
}

# Metric calculation

def calculate_margins(base_price, selling_cost, discount_pct, quantity, region):
    region_factor = REGION_MODIFIER.get(region, 1.0)
    selling_price = base_price * (1 - discount_pct / 100)
    adj_cost = selling_cost / region_factor
    gross_margin = selling_price - adj_cost
    gross_margin_pct = (gross_margin / selling_price) * 100
    total_profit = gross_margin * quantity
    discount_impact_factor = 1 - (discount_pct / 100 * 0.7)
    gross_margin_pct_adj = gross_margin_pct * discount_impact_factor

    return selling_price, adj_cost, gross_margin, gross_margin_pct, gross_margin_pct_adj, total_profit



st.markdown("<br>", unsafe_allow_html=True)
calc_button = st.button("✅ Calculate", type="primary", use_container_width=True)

if calc_button:
    if region == "(Select Region)":
        st.warning("Please select a valid Location Region before calculation.")
    else:
        selling_price, adj_cost, gross_margin, gross_margin_pct, gross_margin_pct_adj, total_profit = calculate_margins(
            base_price, selling_cost, discount_pct, quantity, region
        )

        st.subheader("📊 Calculation Results")
        result_df = pd.DataFrame({
            "Metric": [
                "Selling Price",
                "Adjusted Cost", 
                "Gross Margin", 
                "Gross Margin % (raw)",
                "Gross Margin % (adj for data variation)",
                "Total Profit"
            ],
            "Value": [
                round(selling_price, 2),
                round(adj_cost,2), 
                round(gross_margin,2), 
                round(gross_margin_pct,2), 
                round(gross_margin_pct_adj,2),
                round(total_profit,2)
            ]
        }).set_index("Metric")
        st.dataframe(result_df, use_container_width=True)

#         # Chart: Discount vs Margin
        discounts = list(range(0, 51, 5))
        margins = [calculate_margins(base_price, selling_cost, d, quantity, region)[2] for d in discounts]

        fig, ax = plt.subplots()
        ax.plot(discounts, margins, marker='o', color='green')
        ax.set_xlabel("Discount (%)")
        ax.set_ylabel("Gross Margin (%)")
        ax.set_title(f"Impact of Discount on Gross Margin ({region} Region)")
        st.pyplot(fig)

            # Generate sensitivity curve
#         sens_df = pd.DataFrame({
#             "Discount_%": [i for i in range(0, 51)],
#         })
#         sens_df["Selling_Price"] = base_price * (1 - sens_df["Discount_%"]/100)
#         sens_df["Gross_Margin_%"] = ((sens_df["Selling_Price"] - adj_cost) / sens_df["Selling_Price"]) * 100
#         sens_df["Gross_Margin_%_adj"] = sens_df["Gross_Margin_%"] * (1 - (sens_df["Discount_%"]/100 * 0.7))

        
#         import altair as alt
#         chart = alt.Chart(sens_df).transform_fold(
#             ['Gross_Margin_%', 'Gross_Margin_%_adj'],
#             as_=['Type', 'Margin']
#         ).mark_line(point=True).encode(
#             x='Discount_%:Q',
#             y='Margin:Q',
#             color='Type:N'
#         ).properties(height=400)

#         st.altair_chart(chart, use_container_width=True)

        # Interpretation note
        st.markdown("""
        💡 **How to Interpret This Graph:**  
        - The curve shows how margins decline as discounts increase.  
        - A **steeper drop** means this product is *highly sensitive* to discounting.  
        - Use the curve to find a *safe discount range* that maintains acceptable margins.
        """)

st.markdown("---")
st.caption("Built for AA Sales Associates — enabling smarter, data-driven discounting decisions.")
