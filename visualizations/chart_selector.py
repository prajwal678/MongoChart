from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

class ChartSelector:
    """Utility to select appropriate chart types based on data structure"""
    
    @staticmethod
    def suggest_chart_type(data: List[Dict[str, Any]], x_field: str, y_field: Optional[str] = None) -> str:
        """Suggest an appropriate chart type based on the data structure"""
        if not data:
            return 'bar'  # Default
            
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(data)
        
        # Handle missing fields
        if x_field not in df.columns:
            return 'bar'
            
        if y_field and y_field not in df.columns:
            y_field = None
            
        # Check x-axis cardinality
        x_cardinality = len(df[x_field].unique())
        
        # Analyze x field type
        x_type = ChartSelector.infer_field_type(df[x_field])
        
        # Analyze y field type if available
        y_type = None
        if y_field:
            y_type = ChartSelector.infer_field_type(df[y_field])
        
        # Decision logic for chart type
        if x_type == 'categorical':
            if x_cardinality <= 10:
                return 'pie' if y_field else 'bar'
            else:
                return 'bar'
                
        elif x_type == 'temporal':
            return 'line'
            
        elif x_type == 'numerical':
            if y_field and y_type == 'numerical':
                return 'scatter'
            else:
                return 'histogram'
                
        # Default
        return 'bar'
    
    @staticmethod
    def infer_field_type(series: pd.Series) -> str:
        """Infer the type of a field (numerical, categorical, temporal)"""
        if pd.api.types.is_numeric_dtype(series):
            # Check if it appears to be categorical despite being numeric
            if len(series.unique()) <= 20:
                return 'categorical'
            return 'numerical'
            
        elif pd.api.types.is_datetime64_dtype(series):
            return 'temporal'
            
        # Try to convert to datetime
        try:
            pd.to_datetime(series)
            return 'temporal'
        except:
            pass
            
        return 'categorical' 