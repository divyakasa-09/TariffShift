
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
potential_shift_sectors = pd.read_csv('temp_potential_sectors.csv')
shift_predictions = pd.read_csv('temp_shift_predictions.csv')

# App title
st.title('Manufacturing Shift Analysis: China to India')

# Data summary
st.subheader("Data Summary")
st.write(f"Number of sectors: {len(shift_predictions)}")
st.write(f"Average tariff differential: {potential_shift_sectors['tariff_differential'].mean():.2f}")

# Top sectors
st.subheader("Top 10 Sectors by Shift Probability")
top_sectors = shift_predictions[['ProductOrSector', 'shift_probability']].head(10).copy()
top_sectors['shift_probability'] = top_sectors['shift_probability'].apply(lambda x: f"{x:.2%}")
st.table(top_sectors)

# Visualization
st.subheader("Sector Visualization")
try:
    # Cap values for better visualization
    plot_data = shift_predictions.copy()
    plot_data['tariff_differential'] = plot_data['tariff_differential'].clip(upper=1000)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(plot_data['tariff_differential'], plot_data['shift_probability'], 
               alpha=0.7, s=50)
    ax.set_xlabel('Tariff Differential (capped at 1000)')
    ax.set_ylabel('Shift Probability')
    ax.set_title('Shift Probability vs Tariff Differential')
    st.pyplot(fig)
except Exception as e:
    st.error(f"Error creating visualization: {e}")

# Interactive sector explorer
st.subheader("Sector Explorer")
selected_sector = st.selectbox("Select a sector to explore:", 
                              options=shift_predictions['ProductOrSector'].tolist())

if selected_sector:
    sector_data = shift_predictions[shift_predictions['ProductOrSector'] == selected_sector].iloc[0]
    
    st.write(f"### {selected_sector}")
    st.write(f"**Shift Probability:** {sector_data['shift_probability']:.2%}")
    
    # Format large numbers for better readability
    def format_large_num(num):
        if num >= 1e9:
            return f"${num/1e9:.2f} billion"
        elif num >= 1e6:
            return f"${num/1e6:.2f} million"
        else:
            return f"${num:.2f}"
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Tariff Differential:** {sector_data['tariff_differential']:.2f}")
        st.write(f"**Imports from China:** {format_large_num(sector_data['china_imports_value'])}")
    
    with col2:
        if 'india_imports_value' in sector_data:
            st.write(f"**Imports from India:** {format_large_num(sector_data['india_imports_value'])}")
            
            # Calculate market share
            total = sector_data['china_imports_value'] + sector_data['india_imports_value']
            if total > 0:
                china_share = sector_data['china_imports_value'] / total * 100
                india_share = sector_data['india_imports_value'] / total * 100
                st.write(f"**Market Share:** China {china_share:.1f}%, India {india_share:.1f}%")
