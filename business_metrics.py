"""
Business metrics calculator for automated reporting
Includes universal business KPIs and trend analysis
"""

import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

class BusinessMetrics:
    def __init__(self, data: pd.DataFrame):
        self.data = data.sort_values('Date').reset_index(drop=True)
        if 'Date' in self.data.columns:
            self.data['Date'] = pd.to_datetime(self.data['Date'])

    def calculate_growth_rate(self, column: str):
        """Calculate period-over-period growth rate (last vs previous)."""
        if column not in self.data.columns or len(self.data[column].dropna()) < 2:
            return 0.0
        current = self.data[column].iloc[-1]
        previous = self.data[column].iloc[-2]
        if previous == 0:
            return float('inf') if current != 0 else 0.0
        growth_rate = ((current - previous) / previous) * 100
        return round(growth_rate, 2)

    def calculate_moving_average(self, column: str, window: int = 7):
        """Calculate moving average for trend analysis."""
        if column not in self.data.columns:
            return None
        return self.data[column].rolling(window=window, min_periods=1).mean()

    def generate_trend_chart(self, column: str, title: str):
        """Generate a HTML fragment (Plotly) for the trend chart of a column."""
        if column not in self.data.columns:
            return ''
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data['Date'], y=self.data[column], name=column, line=dict(color='#2E86C1')))
        ma = self.calculate_moving_average(column)
        if ma is not None:
            fig.add_trace(go.Scatter(x=self.data['Date'], y=ma, name=f'{column} (MA)', line=dict(color='#E67E22', dash='dash')))
        fig.update_layout(title=title, xaxis_title='Date', yaxis_title=column, template='simple_white', height=400, margin=dict(t=40,r=20,l=40,b=40))
        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def calculate_kpis(self):
        """Calculate key business metrics and return a dict."""
        kpis = {}
        # Revenue
        if 'Revenue' in self.data.columns:
            kpis['total_revenue'] = float(self.data['Revenue'].sum())
            kpis['avg_daily_revenue'] = float(self.data['Revenue'].mean())
            kpis['revenue_growth'] = self.calculate_growth_rate('Revenue')
        # Sales
        if 'Sales' in self.data.columns:
            kpis['total_sales'] = float(self.data['Sales'].sum())
            kpis['avg_daily_sales'] = float(self.data['Sales'].mean())
            kpis['sales_growth'] = self.calculate_growth_rate('Sales')
        # Customers
        if 'Customer_Count' in self.data.columns:
            kpis['total_customers'] = float(self.data['Customer_Count'].sum())
            kpis['avg_daily_customers'] = float(self.data['Customer_Count'].mean())
            kpis['customer_growth'] = self.calculate_growth_rate('Customer_Count')
            if 'Revenue' in self.data.columns and self.data['Customer_Count'].sum() != 0:
                kpis['avg_revenue_per_customer'] = float(self.data['Revenue'].sum() / self.data['Customer_Count'].sum())
        return kpis

    def generate_summary_html(self):
        """Return an HTML fragment with KPIs and charts to embed in the email template."""
        kpis = self.calculate_kpis()
        parts = []
        # KPI cards
        parts.append('<div class="kpi-container">')
        parts.append('<h3>Key Performance Indicators</h3>')
        parts.append('<div class="kpi-grid">')
        mapping = {
            'total_revenue': ('Total Revenue', '$'),
            'avg_daily_revenue': ('Avg Daily Revenue', '$'),
            'revenue_growth': ('Revenue Growth', '%'),
            'total_sales': ('Total Sales', ''),
            'avg_daily_sales': ('Avg Daily Sales', ''),
            'sales_growth': ('Sales Growth', '%'),
            'total_customers': ('Total Customers', ''),
            'avg_daily_customers': ('Avg Daily Customers', ''),
            'customer_growth': ('Customer Growth', '%'),
            'avg_revenue_per_customer': ('Avg Revenue/Customer', '$')
        }
        for key, (label, prefix) in mapping.items():
            if key in kpis:
                val = kpis[key]
                # format
                if isinstance(val, float):
                    display = f"{prefix}{val:,.2f}" if prefix else f"{val:,.2f}"
                else:
                    display = str(val)
                color = 'green' if 'growth' in key and isinstance(val, (int, float)) and val > 0 else 'red' if 'growth' in key and isinstance(val, (int, float)) and val < 0 else 'black'
                parts.append(f"<div class=\"kpi-card\"><h3>{label}</h3><p style=\"color:{color}\">{display}</p></div>")
        parts.append('</div></div>')
        # Charts
        for col in ['Revenue', 'Sales', 'Customer_Count']:
            if col in self.data.columns:
                parts.append('<div class="chart-container">')
                parts.append(self.generate_trend_chart(col, f'{col} Trend'))
                parts.append('</div>')
        return '\n'.join(parts)
