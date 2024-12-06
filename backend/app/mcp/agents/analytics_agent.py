from typing import Dict, Any
from ..base import AgentContext, AgentState, AgentMessage
from ...services.analytics_service import AnalyticsService
from ...services.email_service import EmailService
from datetime import datetime

class AnalyticsAgent:
    def __init__(self, context: AgentContext, db_session):
        self.context = context
        self.analytics_service = AnalyticsService(db_session)
        self.email_service = EmailService()
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self):
        return {
            "generate_report": self._generate_report,
            "create_visualization": self._create_visualization,
            "send_report": self._send_report,
            "analyze_performance": self._analyze_performance
        }
    
    async def _generate_report(
        self,
        user_id: str,
        date_range: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            return await self.analytics_service.generate_performance_report(
                user_id, date_range
            )
        except Exception as e:
            self.context.state = AgentState.ERROR
            raise Exception(f"Failed to generate report: {str(e)}")
    
    async def _create_visualization(
        self,
        data: Dict[str, Any],
        viz_type: str
    ) -> Dict[str, Any]:
        """Create visualization from analytics data"""
        try:
            return self.analytics_service.create_visualization(data, viz_type)
        except Exception as e:
            self.context.state = AgentState.ERROR
            raise Exception(f"Failed to create visualization: {str(e)}")
    
    async def _send_report(
        self,
        user_email: str,
        report_data: Dict[str, Any]
    ) -> bool:
        """Send analytics report via email"""
        try:
            template_data = {
                'report_data': report_data,
                'dashboard_url': f"{settings.APP_URL}/analytics",
                'date': datetime.utcnow().strftime("%Y-%m-%d")
            }
            return await self.email_service.send_email(
                to_email=user_email,
                subject="Your Performance Report",
                template_name="analytics_report",
                template_data=template_data
            )
        except Exception as e:
            self.context.state = AgentState.ERROR
            raise Exception(f"Failed to send report: {str(e)}")
    
    async def _analyze_performance(
        self,
        user_id: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance metrics and generate insights"""
        insights = []
        
        # Analyze lead metrics
        if metrics['lead_metrics']['total_leads'] > 0:
            conversion_rate = metrics['conversion_rate']
            if conversion_rate < 10:
                insights.append({
                    'type': 'warning',
                    'message': 'Low lead conversion rate. Consider reviewing lead qualification process.'
                })
            elif conversion_rate > 30:
                insights.append({
                    'type': 'success',
                    'message': 'Excellent lead conversion rate!'
                })
        
        # Analyze transaction metrics
        if metrics['transaction_metrics']['total_transactions'] > 0:
            avg_value = metrics['transaction_metrics']['avg_transaction_value']
            if avg_value > 500000:
                insights.append({
                    'type': 'success',
                    'message': 'High average transaction value!'
                })
        
        return {
            'insights': insights,
            'recommendations': self._generate_recommendations(insights)
        }
    
    def _generate_recommendations(self, insights: List[Dict[str, str]]) -> List[str]:
        """Generate recommendations based on insights"""
        recommendations = []
        
        for insight in insights:
            if insight['type'] == 'warning':
                if 'conversion rate' in insight['message'].lower():
                    recommendations.extend([
                        'Review lead qualification criteria',
                        'Implement lead scoring system',
                        'Follow up with leads more frequently'
                    ])
            elif insight['type'] == 'success':
                if 'transaction value' in insight['message'].lower():
                    recommendations.extend([
                        'Focus on luxury market segment',
                        'Create high-value property marketing templates',
                        'Build network with luxury market agents'
                    ])
        
        return recommendations
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Process analytics-related requests"""
        self.context.state = AgentState.WORKING
        
        try:
            action = message.metadata.get('action')
            data = message.metadata.get('data', {})
            
            response = {"status": "success", "data": None}
            
            if action == "generate_report":
                report = await self._generate_report(
                    user_id=data['user_id'],
                    date_range=data.get('date_range', 30)
                )
                
                # Create visualizations
                visualizations = {
                    'leads_trend': await self._create_visualization(
                        report['lead_metrics'], 'leads_over_time'
                    ),
                    'transaction_status': await self._create_visualization(
                        report['transaction_metrics'], 'transactions_by_status'
                    )
                }
                
                # Generate insights
                analysis = await self._analyze_performance(
                    data['user_id'], report
                )
                
                response["data"] = {
                    "report": report,
                    "visualizations": visualizations,
                    "analysis": analysis
                }
                
                # Send report if requested
                if data.get('send_email'):
                    await self._send_report(
                        user_email=data['user_email'],
                        report_data=response["data"]
                    )
            
            self.context.state = AgentState.IDLE
            return AgentMessage(
                content="Task completed",
                metadata=response,
                source_agent=self.context.agent_id
            )
            
        except Exception as e:
            self.context.state = AgentState.ERROR
            return AgentMessage(
                content="Error processing task",
                metadata={"status": "error", "message": str(e)},
                source_agent=self.context.agent_id
            )
