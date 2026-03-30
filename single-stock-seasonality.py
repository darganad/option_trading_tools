import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import warnings

class FridaySeasonalityAnalyzer:
    """
    Stock seasonality analyzer that analyzes patterns from today to upcoming Fridays.
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        
    def get_next_fridays(self, start_date: datetime, num_fridays: int = 4) -> List[datetime]:
        """
        Get the next N Fridays from a given date.
        """
        fridays = []
        current_date = start_date
        
        # Find the next Friday (or today if it's Friday)
        days_until_friday = (4 - current_date.weekday()) % 7
        if days_until_friday == 0 and current_date.hour >= 16:  # If it's Friday after market close
            days_until_friday = 7
            
        next_friday = current_date + timedelta(days=days_until_friday)
        
        # Collect the requested number of Fridays
        for i in range(num_fridays):
            fridays.append(next_friday + timedelta(weeks=i))
            
        return fridays
    
    def get_period_return(self, year: int, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """
        Get r eturn for a specific period in a given year, matching the day pattern.
        """
        try:
            # Calculate the day difference in the original pattern
            day_diff = (end_date - start_date).days
            
            # Create dates for the historical year
            hist_start = start_date.replace(year=year)
            hist_end = hist_start + timedelta(days=day_diff)
            
            # Check if dates are valid
            if hist_end > datetime.now():
                print(f"  Skipping {year}: End date is in the future")
                return None
                
            # Add buffer days for download
            download_start = hist_start - timedelta(days=5)
            download_end = hist_end + timedelta(days=5)
            
            # Download data using yfinance
            print(f"  Downloading data for {year}...")
            stock = yf.Ticker(self.symbol)
            data = stock.history(start=download_start, end=download_end)
            
            if data.empty:
                print(f"  No data available for {year}")
                return None
            
            # Remove timezone by converting to string dates and back
            data.index = pd.to_datetime(data.index.strftime('%Y-%m-%d'))
            
            # Find closest trading days to our target dates
            all_dates = data.index
            
            # Find start date
            start_candidates = all_dates[all_dates >= pd.Timestamp(hist_start)]
            if len(start_candidates) == 0:
                print(f"  No valid start date for {year}")
                return None
            actual_start = start_candidates[0]
            
            # Find end date
            end_candidates = all_dates[all_dates <= pd.Timestamp(hist_end)]
            if len(end_candidates) == 0:
                print(f"  No valid end date for {year}")
                return None
            actual_end = end_candidates[-1]
            
            # Get the period data
            period_data = data.loc[actual_start:actual_end]
            
            if len(period_data) < 2:
                print(f"  Insufficient data points for {year}")
                return None
            
            # Calculate return
            start_price = float(period_data['Close'].iloc[0])
            end_price = float(period_data['Close'].iloc[-1])
            
            if start_price <= 0 or end_price <= 0:
                print(f"  Invalid prices for {year}")
                return None
                
            period_return = ((end_price - start_price) / start_price) * 100
            
            return {
                'year': year,
                'return': period_return,
                'start_price': start_price,
                'end_price': end_price,
                'start_date': actual_start.strftime('%Y-%m-%d'),
                'end_date': actual_end.strftime('%Y-%m-%d'),
                'trading_days': len(period_data)
            }
            
        except Exception as e:
            print(f"  Error processing {year}: {str(e)}")
            return None
    
    def analyze_to_friday_pattern(self, start_date: datetime, friday_date: datetime, 
                                  start_year: int = 2024, end_year: int = 2015) -> Dict:
        """
        Analyze a pattern from a specific date to a Friday across multiple years.
        """
        period_str = f"{start_date.strftime('%m/%d')} to {friday_date.strftime('%m/%d')} (Friday)"
        print(f"\nAnalyzing {self.symbol} from {period_str}")
        print(f"Years: {start_year} to {end_year}")
        print(f"Period length: {(friday_date - start_date).days} days")
        
        # Collect results
        results = []
        
        # Analyze each year
        for year in range(start_year, end_year - 1, -1):
            print(f"\nProcessing year {year}:")
            result = self.get_period_return(year, start_date, friday_date)
            if result:
                results.append(result)
                print(f"  ✓ Return: {result['return']:.2f}%")
        
        # Calculate statistics
        if len(results) < 3:
            return {
                'error': f'Insufficient data: only {len(results)} valid periods found',
                'symbol': self.symbol,
                'period': period_str,
                'results': results
            }
        
        returns = [r['return'] for r in results]
        positive = [r for r in returns if r > 0]
        negative = [r for r in returns if r <= 0]
        
        analysis = {
            'symbol': self.symbol,
            'period': period_str,
            'days_in_period': (friday_date - start_date).days,
            'total_periods': len(results),
            'winning_periods': len(positive),
            'losing_periods': len(negative),
            'win_rate': (len(positive) / len(results)) * 100,
            'results': results,
            'returns': returns
        }
        
        # Basic statistics
        analysis['average_return'] = np.mean(returns)
        analysis['median_return'] = np.median(returns)
        analysis['best_return'] = max(returns)
        analysis['worst_return'] = min(returns)
        analysis['std_deviation'] = np.std(returns, ddof=1)
        
        # Win/loss statistics
        if positive:
            analysis['average_win'] = np.mean(positive)
        if negative:
            analysis['average_loss'] = np.mean(negative)
            
        return analysis
    
    def analyze_friday_patterns(self, num_fridays: int = 4, start_year: int = 2024, 
                               end_year: int = 2015, custom_start_date: Optional[datetime] = None):
        """
        Analyze patterns from today (or custom date) to the next N Fridays.
        """
        start_date = custom_start_date or datetime.now()
        print(f"\n{'='*70}")
        print(f"FRIDAY PATTERN ANALYSIS FOR {self.symbol}")
        print(f"Starting from: {start_date.strftime('%Y-%m-%d %A')}")
        print(f"{'='*70}")
        
        # Get upcoming Fridays
        fridays = self.get_next_fridays(start_date, num_fridays)
        
        all_results = []
        
        for i, friday in enumerate(fridays):
            print(f"\n\n{'*'*60}")
            print(f"PATTERN {i+1}: Today to {friday.strftime('%Y-%m-%d')} ({(friday - start_date).days} days)")
            print(f"{'*'*60}")
            
            analysis = self.analyze_to_friday_pattern(start_date, friday, start_year, end_year)
            all_results.append(analysis)
            self.print_results(analysis)
            
        return all_results
    
    def print_results(self, analysis: Dict):
        """Print analysis results in a formatted way."""
        if 'error' in analysis:
            print(f"\n❌ ERROR: {analysis['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"SEASONALITY ANALYSIS RESULTS")
        print(f"Symbol: {analysis['symbol']}")
        print(f"Period: {analysis['period']} ({analysis['days_in_period']} days)")
        print(f"{'='*60}")
        
        print(f"\nSUMMARY:")
        print(f"Total periods analyzed: {analysis['total_periods']}")
        print(f"Winning periods: {analysis['winning_periods']} ({analysis['win_rate']:.1f}%)")
        print(f"Losing periods: {analysis['losing_periods']} ({100-analysis['win_rate']:.1f}%)")
        
        print(f"\nRETURN STATISTICS:")
        print(f"Average return: {analysis['average_return']:.2f}%")
        print(f"Median return: {analysis['median_return']:.2f}%")
        print(f"Best return: {analysis['best_return']:.2f}%")
        print(f"Worst return: {analysis['worst_return']:.2f}%")
        print(f"Standard deviation: {analysis['std_deviation']:.2f}%")
        
        if 'average_win' in analysis:
            print(f"\nWINNING PERIODS:")
            print(f"Average win: {analysis['average_win']:.2f}%")
            
        if 'average_loss' in analysis:
            print(f"\nLOSING PERIODS:")
            print(f"Average loss: {analysis['average_loss']:.2f}%")
        
        print(f"\nYEAR-BY-YEAR RESULTS:")
        print(f"{'Year':<6} {'Return':>8} {'Start':>12} {'End':>12} {'Period':<22}")
        print("-" * 60)
        
        for result in sorted(analysis['results'], key=lambda x: x['year'], reverse=True):
            print(f"{result['year']:<6} {result['return']:>7.2f}% "
                  f"${result['start_price']:>10.2f} ${result['end_price']:>10.2f} "
                  f"{result['start_date']} to {result['end_date']}")
        
        print(f"\nAll returns: {[round(r, 2) for r in analysis['returns']]}")
    
    def compare_friday_patterns(self, results: List[Dict]):
        """
        Compare multiple Friday pattern results.
        """
        print(f"\n\n{'='*70}")
        print(f"FRIDAY PATTERN COMPARISON")
        print(f"{'='*70}")
        
        print(f"\n{'Pattern':<30} {'Days':>5} {'Win%':>8} {'Avg Ret':>10} {'Best':>10} {'Worst':>10}")
        print("-" * 75)
        
        for result in results:
            if 'error' not in result:
                print(f"{result['period']:<30} {result['days_in_period']:>5} "
                      f"{result['win_rate']:>7.1f}% {result['average_return']:>9.2f}% "
                      f"{result['best_return']:>9.2f}% {result['worst_return']:>9.2f}%")


# Example usage
if __name__ == "__main__":
    # Test with Raymond James Financial (RJF)
    analyzer = FridaySeasonalityAnalyzer('META')
    
    # Analyze patterns to the next 4 Fridays
    results = analyzer.analyze_friday_patterns(
        num_fridays=8,
        start_year=2025,
        end_year=2016
    )
    
    # Compare all Friday patterns
    analyzer.compare_friday_patterns(results)
    
    # You can also analyze from a specific date
    # custom_date = datetime(2024, 9, 1)  # Start from September 1st
    # results = analyzer.analyze_friday_patterns(
    #     num_fridays=3,
    #     start_year=2024,
    #     end_year=2015,
    #     custom_start_date=custom_date
    # )
    
    # Example: Test cross-year pattern (late December)
    # december_date = datetime(2024, 12, 28)
    # results = analyzer.analyze_friday_patterns(
    #     num_fridays=3,
    #     start_year=2023,
    #     end_year=2015,
    #     custom_start_date=december_date
    # )