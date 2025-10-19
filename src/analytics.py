"""
Advanced analytics and visualizations for Time Tracker App
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from typing import Dict, List, Optional, Tuple
from logger import log_error

class AnalyticsEngine:
    """Advanced analytics engine for time tracking data"""
    
    def __init__(self, logs_df: pd.DataFrame, tasks_df: pd.DataFrame):
        self.logs_df = logs_df.copy()
        self.tasks_df = tasks_df.copy()
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare data for analysis"""
        try:
            if not self.logs_df.empty:
                # Convert data types
                self.logs_df['duration_minutes'] = pd.to_numeric(self.logs_df['duration_minutes'], errors='coerce').fillna(0)
                self.logs_df['date'] = pd.to_datetime(self.logs_df['date'], errors='coerce')
                self.logs_df['start_time'] = pd.to_datetime(self.logs_df['start_time'], errors='coerce')
                self.logs_df['end_time'] = pd.to_datetime(self.logs_df['end_time'], errors='coerce')
                
                # Add derived columns
                self.logs_df['weekday'] = self.logs_df['date'].dt.day_name()
                self.logs_df['week'] = self.logs_df['date'].dt.isocalendar().week
                self.logs_df['month'] = self.logs_df['date'].dt.month
                self.logs_df['year'] = self.logs_df['date'].dt.year
                self.logs_df['hour'] = self.logs_df['start_time'].dt.hour
                
        except Exception as e:
            log_error(f"Failed to prepare analytics data: {e}", e)
    
    def get_productivity_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive productivity metrics"""
        try:
            if self.logs_df.empty:
                return {}
                
            metrics = {}
            
            # Basic metrics
            metrics['total_time_hours'] = self.logs_df['duration_minutes'].sum() / 60
            metrics['total_sessions'] = len(self.logs_df)
            metrics['unique_tasks'] = self.logs_df['task'].nunique()
            metrics['avg_session_length'] = self.logs_df['duration_minutes'].mean()
            
            # Time-based metrics
            today = datetime.datetime.now().date()
            this_week = datetime.datetime.now().date() - datetime.timedelta(days=7)
            this_month = datetime.datetime.now().date() - datetime.timedelta(days=30)
            
            metrics['today_time'] = self.logs_df[self.logs_df['date'].dt.date == today]['duration_minutes'].sum() / 60
            metrics['week_time'] = self.logs_df[self.logs_df['date'].dt.date >= this_week]['duration_minutes'].sum() / 60
            metrics['month_time'] = self.logs_df[self.logs_df['date'].dt.date >= this_month]['duration_minutes'].sum() / 60
            
            # Productivity patterns
            if not self.logs_df.empty:
                # Most productive day of week
                weekday_totals = self.logs_df.groupby('weekday')['duration_minutes'].sum()
                metrics['most_productive_day'] = weekday_totals.idxmax() if not weekday_totals.empty else None
                
                # Most productive hour
                hour_totals = self.logs_df.groupby('hour')['duration_minutes'].sum()
                metrics['most_productive_hour'] = hour_totals.idxmax() if not hour_totals.empty else None
                
                # Consistency score (standard deviation of daily totals)
                daily_totals = self.logs_df.groupby('date')['duration_minutes'].sum()
                metrics['consistency_score'] = 1 - (daily_totals.std() / daily_totals.mean()) if daily_totals.mean() > 0 else 0
                
            return metrics
            
        except Exception as e:
            log_error(f"Failed to calculate productivity metrics: {e}", e)
            return {}
    
    def create_time_trend_chart(self) -> go.Figure:
        """Create time trend visualization"""
        try:
            if self.logs_df.empty:
                return self._create_empty_chart("No data available")
                
            # Daily time totals
            daily_totals = self.logs_df.groupby('date')['duration_minutes'].sum().reset_index()
            daily_totals['hours'] = daily_totals['duration_minutes'] / 60
            
            fig = px.line(
                daily_totals, 
                x='date', 
                y='hours',
                title="Daily Time Tracking Trend",
                labels={'hours': 'Hours Worked', 'date': 'Date'}
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='white',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            
            return fig
            
        except Exception as e:
            log_error(f"Failed to create time trend chart: {e}", e)
            return self._create_empty_chart("Error creating chart")
    
    def create_task_distribution_chart(self) -> go.Figure:
        """Create task distribution pie chart"""
        try:
            if self.logs_df.empty:
                return self._create_empty_chart("No data available")
                
            task_totals = self.logs_df.groupby('task')['duration_minutes'].sum().reset_index()
            task_totals['hours'] = task_totals['duration_minutes'] / 60
            
            fig = px.pie(
                task_totals,
                values='hours',
                names='task',
                title="Time Distribution by Task"
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='white'
            )
            
            return fig
            
        except Exception as e:
            log_error(f"Failed to create task distribution chart: {e}", e)
            return self._create_empty_chart("Error creating chart")
    
    def create_productivity_heatmap(self) -> go.Figure:
        """Create productivity heatmap by day of week and hour"""
        try:
            if self.logs_df.empty:
                return self._create_empty_chart("No data available")
                
            # Create pivot table
            heatmap_data = self.logs_df.groupby(['weekday', 'hour'])['duration_minutes'].sum().reset_index()
            heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='duration_minutes').fillna(0)
            
            # Order days properly
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_pivot = heatmap_pivot.reindex([day for day in day_order if day in heatmap_pivot.index])
            
            fig = px.imshow(
                heatmap_pivot,
                title="Productivity Heatmap (Day vs Hour)",
                labels=dict(x="Hour", y="Day", color="Minutes"),
                color_continuous_scale="Viridis"
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='white'
            )
            
            return fig
            
        except Exception as e:
            log_error(f"Failed to create productivity heatmap: {e}", e)
            return self._create_empty_chart("Error creating chart")
    
    def create_session_length_distribution(self) -> go.Figure:
        """Create session length distribution histogram"""
        try:
            if self.logs_df.empty:
                return self._create_empty_chart("No data available")
                
            fig = px.histogram(
                self.logs_df,
                x='duration_minutes',
                title="Session Length Distribution",
                labels={'duration_minutes': 'Session Length (minutes)', 'count': 'Number of Sessions'},
                nbins=20
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='white',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            
            return fig
            
        except Exception as e:
            log_error(f"Failed to create session length distribution: {e}", e)
            return self._create_empty_chart("Error creating chart")
    
    def get_task_performance_analysis(self) -> pd.DataFrame:
        """Get detailed task performance analysis"""
        try:
            if self.logs_df.empty:
                return pd.DataFrame()
                
            analysis = self.logs_df.groupby('task').agg({
                'duration_minutes': ['sum', 'count', 'mean', 'std', 'min', 'max'],
                'date': 'nunique'
            }).round(2)
            
            analysis.columns = ['total_time', 'sessions', 'avg_session', 'std_session', 'min_session', 'max_session', 'days_worked']
            
            # Add efficiency metrics
            analysis['efficiency_score'] = analysis['avg_session'] / analysis['std_session'] if analysis['std_session'].sum() > 0 else 0
            analysis['consistency_score'] = 1 - (analysis['std_session'] / analysis['avg_session']) if analysis['avg_session'].sum() > 0 else 0
            
            return analysis.sort_values('total_time', ascending=False)
            
        except Exception as e:
            log_error(f"Failed to create task performance analysis: {e}", e)
            return pd.DataFrame()
    
    def get_weekly_summary(self) -> pd.DataFrame:
        """Get weekly summary statistics"""
        try:
            if self.logs_df.empty:
                return pd.DataFrame()
                
            weekly_data = self.logs_df.groupby(['year', 'week']).agg({
                'duration_minutes': ['sum', 'count', 'mean'],
                'task': 'nunique'
            }).round(2)
            
            weekly_data.columns = ['total_time', 'sessions', 'avg_session', 'unique_tasks']
            weekly_data['total_hours'] = weekly_data['total_time'] / 60
            
            return weekly_data.reset_index()
            
        except Exception as e:
            log_error(f"Failed to create weekly summary: {e}", e)
            return pd.DataFrame()
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="white")
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        return fig
