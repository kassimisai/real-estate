from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models.lead import Lead
from ..models.transaction import Transaction, TransactionStatus

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_lead_metrics(self, user_id: str, date_range: int = 30) -> Dict[str, Any]:
        """Get lead-related metrics"""
        start_date = datetime.utcnow() - timedelta(days=date_range)
        
        # Query leads
        leads = self.db.query(Lead)\
            .filter(Lead.user_id == user_id,
                   Lead.created_at >= start_date)\
            .all()
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'created_at': lead.created_at,
            'status': lead.status,
            'source': lead.source
        } for lead in leads])
        
        if df.empty:
            return {
                'total_leads': 0,
                'conversion_rate': 0,
                'leads_by_source': {},
                'leads_by_status': {},
                'leads_over_time': []
            }

        # Calculate metrics
        total_leads = len(df)
        leads_by_source = df['source'].value_counts().to_dict()
        leads_by_status = df['status'].value_counts().to_dict()
        
        # Calculate leads over time
        df['date'] = df['created_at'].dt.date
        leads_over_time = df.groupby('date').size().reset_index()
        leads_over_time.columns = ['date', 'count']
        
        return {
            'total_leads': total_leads,
            'leads_by_source': leads_by_source,
            'leads_by_status': leads_by_status,
            'leads_over_time': leads_over_time.to_dict('records')
        }

    async def get_transaction_metrics(self, user_id: str, date_range: int = 30) -> Dict[str, Any]:
        """Get transaction-related metrics"""
        start_date = datetime.utcnow() - timedelta(days=date_range)
        
        # Query transactions
        transactions = self.db.query(Transaction)\
            .filter(Transaction.user_id == user_id,
                   Transaction.created_at >= start_date)\
            .all()
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'created_at': tx.created_at,
            'status': tx.status,
            'price': float(tx.price.replace('$', '').replace(',', ''))
        } for tx in transactions])
        
        if df.empty:
            return {
                'total_transactions': 0,
                'total_value': 0,
                'avg_transaction_value': 0,
                'transactions_by_status': {},
                'transactions_over_time': []
            }

        # Calculate metrics
        total_transactions = len(df)
        total_value = df['price'].sum()
        avg_transaction_value = df['price'].mean()
        transactions_by_status = df['status'].value_counts().to_dict()
        
        # Calculate transactions over time
        df['date'] = df['created_at'].dt.date
        transactions_over_time = df.groupby('date').agg({
            'price': 'sum',
            'status': 'count'
        }).reset_index()
        transactions_over_time.columns = ['date', 'value', 'count']
        
        return {
            'total_transactions': total_transactions,
            'total_value': total_value,
            'avg_transaction_value': avg_transaction_value,
            'transactions_by_status': transactions_by_status,
            'transactions_over_time': transactions_over_time.to_dict('records')
        }

    async def generate_performance_report(self, user_id: str, date_range: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        lead_metrics = await self.get_lead_metrics(user_id, date_range)
        transaction_metrics = await self.get_transaction_metrics(user_id, date_range)
        
        # Calculate additional metrics
        conversion_rate = 0
        if lead_metrics['total_leads'] > 0:
            conversion_rate = (transaction_metrics['total_transactions'] / 
                             lead_metrics['total_leads']) * 100
        
        return {
            'lead_metrics': lead_metrics,
            'transaction_metrics': transaction_metrics,
            'conversion_rate': conversion_rate,
            'report_date': datetime.utcnow(),
            'date_range': date_range
        }

    def create_visualization(self, data: Dict[str, Any], viz_type: str) -> Dict[str, Any]:
        """Create visualization based on analytics data"""
        if viz_type == "leads_over_time":
            df = pd.DataFrame(data['leads_over_time'])
            fig = px.line(df, x='date', y='count', title='Leads Over Time')
        
        elif viz_type == "transactions_by_status":
            df = pd.DataFrame(list(data['transactions_by_status'].items()),
                            columns=['status', 'count'])
            fig = px.pie(df, values='count', names='status',
                        title='Transactions by Status')
        
        elif viz_type == "transaction_value_trend":
            df = pd.DataFrame(data['transactions_over_time'])
            fig = px.bar(df, x='date', y='value',
                        title='Transaction Value Over Time')
        
        else:
            raise ValueError(f"Unsupported visualization type: {viz_type}")
        
        return fig.to_dict()
