# import yfinance as yf
# from datetime import datetime, timedelta
# import pandas as pd
# import numpy as np
# from typing import Optional, Dict, List
# import warnings
# from tabulate import tabulate

# class FridaySeasonalityAnalyzer:
#     """
#     Stock seasonality analyzer that analyzes patterns from today to upcoming Fridays.
#     """
    
#     def __init__(self, symbol: str):
#         self.symbol = symbol.upper()
        
#     def get_next_fridays(self, start_date: datetime, num_fridays: int = 4) -> List[datetime]:
#         """
#         Get the next N Fridays from a given date.
#         """
#         fridays = []
#         current_date = start_date
        
#         # Find the next Friday (or today if it's Friday)
#         days_until_friday = (4 - current_date.weekday()) % 7
#         if days_until_friday == 0 and current_date.hour >= 16:  # If it's Friday after market close
#             days_until_friday = 7
            
#         next_friday = current_date + timedelta(days=days_until_friday)
        
#         # Collect the requested number of Fridays
#         for i in range(num_fridays):
#             fridays.append(next_friday + timedelta(weeks=i))
            
#         return fridays
    
#     def get_period_return(self, year: int, start_date: datetime, end_date: datetime, silent: bool = False) -> Optional[Dict]:
#         """
#         Get return for a specific period in a given year, matching the day pattern.
#         """
#         try:
#             # Calculate the day difference in the original pattern
#             day_diff = (end_date - start_date).days
            
#             # Create dates for the historical year
#             hist_start = start_date.replace(year=year)
#             hist_end = hist_start + timedelta(days=day_diff)
            
#             # Check if dates are valid
#             if hist_end > datetime.now():
#                 if not silent:
#                     print(f"  Skipping {year}: End date is in the future")
#                 return None
                
#             # Add buffer days for download
#             download_start = hist_start - timedelta(days=5)
#             download_end = hist_end + timedelta(days=5)
            
#             # Download data using yfinance
#             if not silent:
#                 print(f"  Downloading data for {year}...")
#             stock = yf.Ticker(self.symbol)
#             data = stock.history(start=download_start, end=download_end)
            
#             if data.empty:
#                 if not silent:
#                     print(f"  No data available for {year}")
#                 return None
            
#             # Remove timezone by converting to string dates and back
#             data.index = pd.to_datetime(data.index.strftime('%Y-%m-%d'))
            
#             # Find closest trading days to our target dates
#             all_dates = data.index
            
#             # Find start date
#             start_candidates = all_dates[all_dates >= pd.Timestamp(hist_start)]
#             if len(start_candidates) == 0:
#                 if not silent:
#                     print(f"  No valid start date for {year}")
#                 return None
#             actual_start = start_candidates[0]
            
#             # Find end date
#             end_candidates = all_dates[all_dates <= pd.Timestamp(hist_end)]
#             if len(end_candidates) == 0:
#                 if not silent:
#                     print(f"  No valid end date for {year}")
#                 return None
#             actual_end = end_candidates[-1]
            
#             # Get the period data
#             period_data = data.loc[actual_start:actual_end]
            
#             if len(period_data) < 2:
#                 if not silent:
#                     print(f"  Insufficient data points for {year}")
#                 return None
            
#             # Calculate return
#             start_price = float(period_data['Close'].iloc[0])
#             end_price = float(period_data['Close'].iloc[-1])
            
#             if start_price <= 0 or end_price <= 0:
#                 if not silent:
#                     print(f"  Invalid prices for {year}")
#                 return None
                
#             period_return = ((end_price - start_price) / start_price) * 100
            
#             return {
#                 'year': year,
#                 'return': period_return,
#                 'start_price': start_price,
#                 'end_price': end_price,
#                 'start_date': actual_start.strftime('%Y-%m-%d'),
#                 'end_date': actual_end.strftime('%Y-%m-%d'),
#                 'trading_days': len(period_data)
#             }
            
#         except Exception as e:
#             if not silent:
#                 print(f"  Error processing {year}: {str(e)}")
#             return None
    
#     def analyze_to_friday_pattern(self, start_date: datetime, friday_date: datetime, 
#                                   start_year: int = 2024, end_year: int = 2015, silent: bool = False) -> Dict:
#         """
#         Analyze a pattern from a specific date to a Friday across multiple years.
#         """
#         period_str = f"{start_date.strftime('%m/%d')} to {friday_date.strftime('%m/%d')} (Friday)"
#         if not silent:
#             print(f"\nAnalyzing {self.symbol} from {period_str}")
#             print(f"Years: {start_year} to {end_year}")
#             print(f"Period length: {(friday_date - start_date).days} days")
        
#         # Collect results
#         results = []
        
#         # Analyze each year
#         for year in range(start_year, end_year - 1, -1):
#             if not silent:
#                 print(f"\nProcessing year {year}:")
#             result = self.get_period_return(year, start_date, friday_date, silent)
#             if result:
#                 results.append(result)
#                 if not silent:
#                     print(f"  ✓ Return: {result['return']:.2f}%")
        
#         # Calculate statistics
#         if len(results) < 3:
#             return {
#                 'error': f'Insufficient data: only {len(results)} valid periods found',
#                 'symbol': self.symbol,
#                 'period': period_str,
#                 'results': results
#             }
        
#         returns = [r['return'] for r in results]
#         positive = [r for r in returns if r > 0]
#         negative = [r for r in returns if r <= 0]
        
#         analysis = {
#             'symbol': self.symbol,
#             'period': period_str,
#             'days_in_period': (friday_date - start_date).days,
#             'total_periods': len(results),
#             'winning_periods': len(positive),
#             'losing_periods': len(negative),
#             'win_rate': (len(positive) / len(results)) * 100,
#             'results': results,
#             'returns': returns
#         }
        
#         # Basic statistics
#         analysis['average_return'] = np.mean(returns)
#         analysis['median_return'] = np.median(returns)
#         analysis['best_return'] = max(returns)
#         analysis['worst_return'] = min(returns)
#         analysis['std_deviation'] = np.std(returns, ddof=1)
        
#         # Win/loss statistics
#         if positive:
#             analysis['average_win'] = np.mean(positive)
#         if negative:
#             analysis['average_loss'] = np.mean(negative)
            
#         return analysis
    
#     def get_win_rates_for_fridays(self, num_fridays: int = 3, start_year: int = 2024, 
#                                   end_year: int = 2015, custom_start_date: Optional[datetime] = None) -> tuple:
#         """
#         Get win rates for the next N Fridays. Returns a tuple of (win_rates, date_ranges).
#         """
#         start_date = custom_start_date or datetime.now()
#         fridays = self.get_next_fridays(start_date, num_fridays)
        
#         win_rates = []
#         date_ranges = []
        
#         for friday in fridays:
#             analysis = self.analyze_to_friday_pattern(start_date, friday, start_year, end_year, silent=True)
#             if 'error' not in analysis:
#                 win_rates.append(analysis['win_rate'])
#             else:
#                 win_rates.append(0.0)  # Default to 0 if insufficient data
            
#             # Create date range string
#             start_str = start_date.strftime('%m%d')
#             end_str = friday.strftime('%m%d')
#             date_ranges.append(f'{start_str}-{end_str}')
                
#         return win_rates, date_ranges
    
#     def print_results(self, analysis: Dict):
#         """Print analysis results in a formatted way."""
#         if 'error' in analysis:
#             print(f"\n❌ ERROR: {analysis['error']}")
#             return
        
#         print(f"\n{'='*60}")
#         print(f"SEASONALITY ANALYSIS RESULTS")
#         print(f"Symbol: {analysis['symbol']}")
#         print(f"Period: {analysis['period']} ({analysis['days_in_period']} days)")
#         print(f"{'='*60}")
        
#         print(f"\nSUMMARY:")
#         print(f"Total periods analyzed: {analysis['total_periods']}")
#         print(f"Winning periods: {analysis['winning_periods']} ({analysis['win_rate']:.1f}%)")
#         print(f"Losing periods: {analysis['losing_periods']} ({100-analysis['win_rate']:.1f}%)")
        
#         print(f"\nRETURN STATISTICS:")
#         print(f"Average return: {analysis['average_return']:.2f}%")
#         print(f"Median return: {analysis['median_return']:.2f}%")
#         print(f"Best return: {analysis['best_return']:.2f}%")
#         print(f"Worst return: {analysis['worst_return']:.2f}%")
#         print(f"Standard deviation: {analysis['std_deviation']:.2f}%")
        
#         if 'average_win' in analysis:
#             print(f"\nWINNING PERIODS:")
#             print(f"Average win: {analysis['average_win']:.2f}%")
            
#         if 'average_loss' in analysis:
#             print(f"\nLOSING PERIODS:")
#             print(f"Average loss: {analysis['average_loss']:.2f}%")


# def analyze_multiple_stocks(symbols: List[str], 
#                           num_fridays: int = 3,
#                           start_year: int = 2024,
#                           end_year: int = 2015,
#                           custom_start_date: Optional[datetime] = None) -> pd.DataFrame:
#     """
#     Analyze multiple stocks and return results as a DataFrame.
    
#     Args:
#         symbols: List of stock symbols to analyze
#         num_fridays: Number of Fridays to analyze (default: 3)
#         start_year: Starting year for historical analysis
#         end_year: Ending year for historical analysis
#         custom_start_date: Optional custom start date
        
#     Returns:
#         DataFrame with stock names and win percentages for each Friday
#     """
#     results = []
#     start_date = custom_start_date or datetime.now()
    
#     # Pre-calculate the date ranges for column headers
#     temp_analyzer = FridaySeasonalityAnalyzer('TEMP')
#     fridays = temp_analyzer.get_next_fridays(start_date, num_fridays)
    
#     # Create column headers with date ranges
#     column_headers = ['Stock']
#     for friday in fridays:
#         start_str = start_date.strftime('%m%d')
#         end_str = friday.strftime('%m%d')
#         column_headers.append(f'{start_str}-{end_str}')
    
#     print(f"Analyzing {len(symbols)} stocks for next {num_fridays} Fridays...\n")
#     print(f"Date ranges: {', '.join(column_headers[1:])}\n")
    
#     for symbol in symbols:
#         print(f"Processing {symbol}...")
#         try:
#             analyzer = FridaySeasonalityAnalyzer(symbol)
#             win_rates, _ = analyzer.get_win_rates_for_fridays(num_fridays, start_year, end_year, custom_start_date)
            
#             # Create row for this stock
#             row_data = [symbol] + win_rates
#             results.append(row_data)
            
#         except Exception as e:
#             print(f"Error processing {symbol}: {str(e)}")
#             # Add row with zeros for failed stocks
#             row_data = [symbol] + [0.0] * num_fridays
#             results.append(row_data)
    
#     # Create DataFrame with proper column names
#     df = pd.DataFrame(results, columns=column_headers)
#     return df


# def print_results_table(df: pd.DataFrame):
#     """
#     Print the results in a nicely formatted table.
#     """
#     print("\n" + "="*70)
#     print("FRIDAY SEASONALITY ANALYSIS RESULTS")
#     print("="*70)
    
#     # Convert DataFrame to list of lists for tabulate
#     headers = df.columns.tolist()
#     rows = df.values.tolist()
    
#     print(tabulate(rows, headers=headers, tablefmt='grid', floatfmt='.1f'))
    
#     # Also print simple format
#     print("\n\nSimple Table Format:")
#     print("-" * (15 + 15 * (len(df.columns) - 1)))
    
#     # Print header
#     header_str = "Stock Name".ljust(12) + " | "
#     for col in df.columns[1:]:
#         header_str += col.center(10) + " | "
#     print(header_str.rstrip(" | "))
#     print("-" * (15 + 15 * (len(df.columns) - 1)))
    
#     # Print each row
#     for _, row in df.iterrows():
#         row_str = row['Stock'].ljust(12) + " | "
#         for col in df.columns[1:]:
#             value = f"{row[col]:.1f}%" if isinstance(row[col], (int, float)) else str(row[col])
#             row_str += value.center(10) + " | "
#         print(row_str.rstrip(" | "))


# # Example usage
# if __name__ == "__main__":
#     # Define the stocks you want to analyze
#     stocks = ['ADBE', 'PANW', 'NVDA', 'AAPL', 'MSFT', 'GOOGL', 'META', 'TSLA']
    
#     # Run analysis for multiple stocks
#     df_results = analyze_multiple_stocks(
#         symbols=stocks,
#         num_fridays=10,  # Analyze next 3 Fridays
#         start_year=2024,
#         end_year=2015
#     )
    
#     # Print results in table format
#     print_results_table(df_results)
    
#     # You can also save to CSV
#     df_results.to_csv('friday_seasonality_results.csv', index=False)
#     print("\nResults saved to 'friday_seasonality_results.csv'")



import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import warnings
from tabulate import tabulate

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
    
    def get_period_return(self, year: int, start_date: datetime, end_date: datetime, silent: bool = False) -> Optional[Dict]:
        """
        Get return for a specific period in a given year, matching the day pattern.
        """
        try:
            # Calculate the day difference in the original pattern
            day_diff = (end_date - start_date).days
            
            # Create dates for the historical year
            hist_start = start_date.replace(year=year)
            hist_end = hist_start + timedelta(days=day_diff)
            
            # Check if dates are valid
            if hist_end > datetime.now():
                if not silent:
                    print(f"  Skipping {year}: End date is in the future")
                return None
                
            # Add buffer days for download
            download_start = hist_start - timedelta(days=5)
            download_end = hist_end + timedelta(days=5)
            
            # Download data using yfinance
            if not silent:
                print(f"  Downloading data for {year}...")
            stock = yf.Ticker(self.symbol)
            data = stock.history(start=download_start, end=download_end)
            
            if data.empty:
                if not silent:
                    print(f"  No data available for {year}")
                return None
            
            # Remove timezone by converting to string dates and back
            data.index = pd.to_datetime(data.index.strftime('%Y-%m-%d'))
            
            # Find closest trading days to our target dates
            all_dates = data.index
            
            # Find start date
            start_candidates = all_dates[all_dates >= pd.Timestamp(hist_start)]
            if len(start_candidates) == 0:
                if not silent:
                    print(f"  No valid start date for {year}")
                return None
            actual_start = start_candidates[0]
            
            # Find end date
            end_candidates = all_dates[all_dates <= pd.Timestamp(hist_end)]
            if len(end_candidates) == 0:
                if not silent:
                    print(f"  No valid end date for {year}")
                return None
            actual_end = end_candidates[-1]
            
            # Get the period data
            period_data = data.loc[actual_start:actual_end]
            
            if len(period_data) < 2:
                if not silent:
                    print(f"  Insufficient data points for {year}")
                return None
            
            # Calculate return
            start_price = float(period_data['Close'].iloc[0])
            end_price = float(period_data['Close'].iloc[-1])
            
            if start_price <= 0 or end_price <= 0:
                if not silent:
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
            if not silent:
                print(f"  Error processing {year}: {str(e)}")
            return None
    
    def analyze_to_friday_pattern(self, start_date: datetime, friday_date: datetime, 
                                  start_year: int = 2024, end_year: int = 2015, silent: bool = False) -> Dict:
        """
        Analyze a pattern from a specific date to a Friday across multiple years.
        """
        period_str = f"{start_date.strftime('%m/%d')} to {friday_date.strftime('%m/%d')} (Friday)"
        if not silent:
            print(f"\nAnalyzing {self.symbol} from {period_str}")
            print(f"Years: {start_year} to {end_year}")
            print(f"Period length: {(friday_date - start_date).days} days")
        
        # Collect results
        results = []
        
        # Analyze each year
        for year in range(start_year, end_year - 1, -1):
            if not silent:
                print(f"\nProcessing year {year}:")
            result = self.get_period_return(year, start_date, friday_date, silent)
            if result:
                results.append(result)
                if not silent:
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
    
    def get_win_rates_for_fridays(self, num_fridays: int = 3, start_year: int = 2024, 
                                  end_year: int = 2015, custom_start_date: Optional[datetime] = None) -> tuple:
        """
        Get win rates for the next N Fridays. Returns a tuple of (win_rates, date_ranges).
        """
        start_date = custom_start_date or datetime.now()
        fridays = self.get_next_fridays(start_date, num_fridays)
        
        win_rates = []
        date_ranges = []
        
        for friday in fridays:
            analysis = self.analyze_to_friday_pattern(start_date, friday, start_year, end_year, silent=True)
            if 'error' not in analysis:
                win_rates.append(analysis['win_rate'])
            else:
                win_rates.append(0.0)  # Default to 0 if insufficient data
            
            # Create date range string
            start_str = start_date.strftime('%m%d')
            end_str = friday.strftime('%m%d')
            date_ranges.append(f'{start_str}-{end_str}')
                
        return win_rates, date_ranges
    
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


def analyze_multiple_stocks(symbols: List[str], 
                          num_fridays: int = 3,
                          start_year: int = 2024,
                          end_year: int = 2015,
                          custom_start_date: Optional[datetime] = None) -> pd.DataFrame:
    """
    Analyze multiple stocks and return results as a DataFrame.
    
    Args:
        symbols: List of stock symbols to analyze
        num_fridays: Number of Fridays to analyze (default: 3)
        start_year: Starting year for historical analysis
        end_year: Ending year for historical analysis
        custom_start_date: Optional custom start date
        
    Returns:
        DataFrame with stock names and win percentages for each Friday
    """
    results = []
    start_date = custom_start_date or datetime.now()
    
    # Pre-calculate the date ranges for column headers
    temp_analyzer = FridaySeasonalityAnalyzer('TEMP')
    fridays = temp_analyzer.get_next_fridays(start_date, num_fridays)
    
    # Create column headers with date ranges
    column_headers = ['Stock']
    for friday in fridays:
        start_str = start_date.strftime('%m%d')
        end_str = friday.strftime('%m%d')
        column_headers.append(f'{start_str}-{end_str}')
    
    print(f"Analyzing {len(symbols)} stocks for next {num_fridays} Fridays...\n")
    print(f"Date ranges: {', '.join(column_headers[1:])}\n")
    
    for symbol in symbols:
        print(f"Processing {symbol}...")
        try:
            analyzer = FridaySeasonalityAnalyzer(symbol)
            win_rates, _ = analyzer.get_win_rates_for_fridays(num_fridays, start_year, end_year, custom_start_date)
            
            # Create row for this stock
            row_data = [symbol] + win_rates
            results.append(row_data)
            
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            # Add row with zeros for failed stocks
            row_data = [symbol] + [0.0] * num_fridays
            results.append(row_data)
    
    # Create DataFrame with proper column names
    df = pd.DataFrame(results, columns=column_headers)
    return df


def print_results_table(df: pd.DataFrame):
    """
    Print the results in a nicely formatted table.
    """
    print("\n" + "="*70)
    print("FRIDAY SEASONALITY ANALYSIS RESULTS")
    print("="*70)
    
    # Convert DataFrame to list of lists for tabulate
    headers = df.columns.tolist()
    rows = df.values.tolist()
    
    print(tabulate(rows, headers=headers, tablefmt='grid', floatfmt='.1f'))
    
    # Also print simple format
    print("\n\nSimple Table Format:")
    print("-" * (15 + 15 * (len(df.columns) - 1)))
    
    # Print header
    header_str = "Stock Name".ljust(12) + " | "
    for col in df.columns[1:]:
        header_str += col.center(10) + " | "
    print(header_str.rstrip(" | "))
    print("-" * (15 + 15 * (len(df.columns) - 1)))
    
    # Print each row
    for _, row in df.iterrows():
        row_str = row['Stock'].ljust(12) + " | "
        for col in df.columns[1:]:
            value = f"{row[col]:.1f}%" if isinstance(row[col], (int, float)) else str(row[col])
            row_str += value.center(10) + " | "
        print(row_str.rstrip(" | "))


def create_html_report(df: pd.DataFrame, filename: str = 'friday_seasonality_report.html'):
    """
    Create an HTML report with color-coded values.
    Green for values >= 80, Red for values < 30
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Friday Seasonality Analysis</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                max-width: 800px;
                margin: 20px auto;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            th {
                background-color: #4a4a4a;
                color: white;
                padding: 12px;
                text-align: center;
                font-weight: bold;
            }
            td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .high-win {
                color: #0d7a0d;
                font-weight: bold;
                background-color: #d4f5d4;
            }
            .low-win {
                color: #a00000;
                font-weight: bold;
                background-color: #ffd4d4;
            }
            .stock-name {
                font-weight: bold;
                text-align: left;
                background-color: #f0f0f0;
            }
            .legend {
                text-align: center;
                margin: 20px;
                font-size: 14px;
            }
            .legend span {
                margin: 0 10px;
                padding: 5px 10px;
                border-radius: 3px;
            }
            .timestamp {
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Friday Seasonality Analysis Results</h1>
        <table>
            <tr>
    """
    
    # Add headers
    for col in df.columns:
        html_content += f"<th>{col}</th>"
    html_content += "</tr>"
    
    # Add data rows
    for _, row in df.iterrows():
        html_content += "<tr>"
        html_content += f'<td class="stock-name">{row["Stock"]}</td>'
        
        for col in df.columns[1:]:
            value = row[col]
            if isinstance(value, (int, float)):
                if value >= 80:
                    cell_class = "high-win"
                elif value < 30:
                    cell_class = "low-win"
                else:
                    cell_class = ""
                html_content += f'<td class="{cell_class}">{value:.1f}%</td>'
            else:
                html_content += f'<td>{value}</td>'
        
        html_content += "</tr>"
    
    html_content += f"""
        </table>
        <div class="legend">
            <span class="high-win">Green = 80% or higher</span>
            <span class="low-win">Red = Below 30%</span>
        </div>
        <div class="timestamp">
            Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w') as f:
        f.write(html_content)
    
    print(f"\nHTML report saved to '{filename}'")


# Example usage
if __name__ == "__main__":
    # Define the stocks you want to analyze


    energy = ['AM', 'APA', 'AR', 'BKR', 'BP', 'CAPL', 'CCJ', 'CHK', 'CHRD', 'CHX', 'CNQ', 'CNXM', 'COP', 'CQP', 'CTRA', 'CVE', 'CVI', 'CVX', 'DCP', 'DINO', 'DK', 'DNN', 'DO', 'DVN', 'E', 'EC', 'ENB', 'EOG', 'EPD', 'EQNR', 'EQT', 'ET', 'FANG', 'FTI', 'GLP', 'HAL', 'HES', 'HESM', 'HFC', 'HP', 'KMI', 'LEU', 'LNG', 'MGY', 'MPC', 'MPLX', 'MRO', 'MTDR', 'NBR', 'NE', 'NOG', 'NOV', 'NXE', 'OKE', 'OVV', 'OXY', 'PAA', 'PAGP', 'PARR', 'PBA', 'PBF', 'PBR', 'PDCE', 'PSX', 'PTEN', 'RIG', 'RRC', 'SHEL', 'SHLX', 'SLB', 'SM', 'SU', 'TRGP', 'TRP', 'TS', 'TTE', 'UEC', 'URA', 'URNM', 'UUUU', 'VAL', 'VLO', 'WES', 'WGP', 'WHD', 'WMB', 'XOM', 'YPF']

    materials = ['AA', 'AEM', 'AGI', 'ALB', 'AMCR', 'APD', 'ASH', 'ATI', 'ATR', 'AU', 'AVNT', 'AVY', 'AXTA', 'B', 'BERY', 'BHP', 'BLL', 'BTG', 'CBT', 'CC', 'CCK', 'CDE', 'CE', 'CLF', 'CLW', 'CMC', 'CRH', 'CRS', 'CX', 'DD', 'DOW', 'ECL', 'EGO', 'EMN', 'EXP', 'FCX', 'FNV', 'FUL', 'GCP', 'GEF', 'GFI', 'GOLD', 'HL', 'HUN', 'IAG', 'IP', 'ITE', 'KGC', 'KRO', 'KS', 'KWR', 'LAC', 'LIN', 'LYB', 'MLM', 'MP', 'MT', 'NEM', 'NEU', 'NUE', 'OI', 'OLN', 'OR', 'PAAS', 'PKG', 'PPG', 'RIO', 'RPM', 'RS', 'RYN', 'SCCO', 'SEE', 'SHW', 'SLGN', 'SLVM', 'SON', 'SQM', 'SSRM', 'STLD', 'SUM', 'SW', 'TECK', 'TRS', 'USLM', 'VALE', 'VMC', 'WPM', 'WRK', 'WY', 'X']

    industrials = ['A', 'AAL', 'ABG', 'ACM', 'ACN', 'AER', 'AGCO', 'AIR', 'AL', 'ALK', 'AME', 'AN', 'AOS', 'APG', 'APH', 'ARCB', 'AWI', 'AXON', 'AYI', 'AZEK', 'BA', 'BAH', 'BE', 'BEP', 'BLDR', 'BMC', 'BWXT', 'CACI', 'CAR', 'CARR', 'CAT', 'CHRW', 'CLH', 'CMI', 'CMRE', 'CNH', 'CNI', 'CP', 'CSX', 'CW', 'CWST', 'DAC', 'DAL', 'DE', 'DOOR', 'DOV', 'DSX', 'DY', 'ECOL', 'EGLE', 'EME', 'EMR', 'ENPH', 'ERJ', 'ETN', 'EXPD', 'FDX', 'FLR', 'FSLR', 'FTV', 'GATX', 'GBX', 'GD', 'GE', 'GEV', 'GFL', 'GGG', 'GIC', 'GLW', 'GNK', 'GNRC', 'GOGL', 'GPI', 'GSL', 'GVA', 'GXO', 'H', 'HA', 'HEI', 'HII', 'HON', 'HRI', 'HSIC', 'HTLD', 'HUBB', 'HURN', 'HWM', 'ICFI', 'IR', 'IT', 'ITW', 'J', 'JBHT', 'JBLU', 'JCI', 'KBR', 'KEX', 'KNX', 'KSU', 'KTOS', 'LAD', 'LDOS', 'LHX', 'LII', 'LMT', 'LPX', 'LSTR', 'LUV', 'MAN', 'MANT', 'MAS', 'MATX', 'MESA', 'MMM', 'MOG.A', 'MTZ', 'NMM', 'NOC', 'NSC', 'NSIT', 'NVT', 'OC', 'ODFL', 'OTIS', 'PAG', 'PCAR', 'PH', 'PWR', 'RHI', 'ROK', 'ROP', 'RSG', 'RTX', 'RUN', 'SAH', 'SAIA', 'SAIC', 'SAVE', 'SEDG', 'SFL', 'SITE', 'SKYW', 'SNDR', 'SNX', 'SPR', 'SRCL', 'STNG', 'STRL', 'SWK', 'TDG', 'TEL', 'TREX', 'TRN', 'TT', 'TTC', 'TTEK', 'TXT', 'UAL', 'UFI', 'UHAL', 'UNP', 'UPS', 'URI', 'VRT', 'WAB', 'WCC', 'WCN', 'WERN', 'WM', 'WSC', 'WWD', 'XPO', 'XYL', 'ZIM']

    consumer_discretionary = ['AAP', 'ABNB', 'ADNT', 'AEO', 'ALV', 'AMC', 'ANF', 'APTV', 'ASO', 'AXL', 'AZO', 'BABA', 'BBWI', 'BBY', 'BC', 'BEKE', 'BHR', 'BJRI', 'BKE', 'BKNG', 'BLMN', 'BROS', 'BURL', 'BWA', 'BYD', 'BZH', 'CAKE', 'CAL', 'CAVA', 'CCL', 'CCS', 'CHDN', 'CHH', 'CHWY', 'CMCSA', 'CMG', 'CNK', 'COLM', 'CPNG', 'CPRI', 'CPS', 'CRI', 'CROX', 'CVNA', 'CWH', 'CWT', 'CZR', 'DAN', 'DDS', 'DECK', 'DENN', 'DFH', 'DHI', 'DIN', 'DIS', 'DKS', 'DPZ', 'DRH', 'DRI', 'EAT', 'EDR', 'EXPE', 'EXPR', 'F', 'FIVE', 'FL', 'FLUT', 'FLWS', 'FND', 'FOX', 'FOXA', 'FSR', 'FTCH', 'GDEN', 'GIII', 'GM', 'GME', 'GNTX', 'GOOS', 'GPS', 'GRBK', 'GTX', 'H', 'HBI', 'HD', 'HIBB', 'HLT', 'HMC', 'HOG', 'HST', 'HZO', 'IHG', 'IMAX', 'JACK', 'JD', 'JWN', 'KBH', 'KSS', 'KTB', 'LCID', 'LCII', 'LEA', 'LEN', 'LESL', 'LGIH', 'LI', 'LL', 'LOW', 'LVS', 'LYV', 'M', 'MAR', 'MBUU', 'MCD', 'MCFT', 'MCRI', 'MDC', 'MELI', 'MGA', 'MGM', 'MHO', 'MOD', 'MSGS', 'MTH', 'NCLH', 'NIO', 'NKE', 'NVR', 'NYT', 'ONON', 'ORLY', 'OSTK', 'OXM', 'PARA', 'PDD', 'PENN', 'PHM', 'PII', 'PK', 'PLAY', 'PLCE', 'PLYA', 'POOL', 'PTRA', 'PVH', 'QSR', 'RACE', 'RCI', 'RCL', 'REAL', 'RH', 'RIVN', 'RL', 'RLJ', 'ROST', 'RRGB', 'RRR', 'SBUX', 'SCVL', 'SE', 'SG', 'SHAK', 'SHO', 'SHOO', 'SIG', 'SKX', 'SKY', 'STLA', 'SUP', 'THO', 'THRM', 'TJX', 'TKO', 'TM', 'TMHC', 'TOL', 'TPH', 'TPR', 'TRV', 'TSCO', 'TXRH', 'ULTA', 'URBN', 'VC', 'VFC', 'VIK', 'VIPS', 'VNE', 'VSCO', 'W', 'WBD', 'WGO', 'WH', 'WING', 'WMG', 'WSM', 'WWE', 'WWW', 'WYNN', 'XHR', 'XPEV', 'YUM', 'YUMC']

    consumer_staples = ['ACI', 'ADM', 'ANDE', 'BF.A', 'BF.B', 'BG', 'BGS', 'BJ', 'BREW', 'BTI', 'BUD', 'CAG', 'CALM', 'CCU', 'CELH', 'CF', 'CHD', 'CHEF', 'CL', 'CLX', 'COST', 'COTY', 'CPB', 'CTVA', 'DAR', 'DEO', 'DG', 'DLTR', 'DOLE', 'EL', 'ELF', 'ENR', 'FDP', 'FIVE', 'FLO', 'FMC', 'FMX', 'GIS', 'GO', 'HRL', 'HSY', 'IMBB', 'IMKTA', 'INGR', 'IPAR', 'K', 'KDP', 'KHC', 'KMB', 'KO', 'KOF', 'KR', 'KVUE', 'LNDC', 'MDLZ', 'MKC', 'MNST', 'MO', 'MOS', 'NTR', 'NUS', 'PEP', 'PG', 'PM', 'POST', 'PRGO', 'REV', 'SAM', 'SFM', 'SJM', 'SMG', 'SMPL', 'SPB', 'SPTN', 'STZ', 'SYY', 'TAP', 'TGT', 'THS', 'TPB', 'TSN', 'UNFI', 'USFD', 'VGR', 'VLGEA', 'WBA', 'WMT']

    healthcare = ['A', 'ABBV', 'ABT', 'ACHC', 'ALGN', 'ALNY', 'AMGN', 'AMWL', 'AORT', 'AXNX', 'AZN', 'BAX', 'BDX', 'BIIB', 'BIO', 'BKD', 'BMRN', 'BMY', 'BNTX', 'BRKR', 'BSX', 'CAH', 'CERT', 'CI', 'CNC', 'COR', 'CRL', 'CVS', 'CYH', 'DGX', 'DHR', 'DOCS', 'DVA', 'ELV', 'ENSG', 'EW', 'EXEL', 'GILD', 'GMED', 'GSK', 'HAE', 'HCA', 'HIMS', 'HLN', 'HOLX', 'HUM', 'IART', 'ICLR', 'ILMN', 'INCY', 'IQV', 'ISRG', 'JAZZ', 'JNJ', 'LH', 'LIVN', 'LLY', 'MCK', 'MD', 'MDT', 'MEDP', 'MOH', 'MRK', 'MRNA', 'MTD', 'NBIX', 'NHC', 'NUVA', 'NVCR', 'NVO', 'NVS', 'NVST', 'OGN', 'PBH', 'PCVX', 'PEN', 'PFE', 'PHR', 'PKI', 'PNTG', 'PODD', 'PRCT', 'PRGO', 'REGN', 'RMD', 'RNA', 'SEM', 'SGEN', 'SGRY', 'SILK', 'SNY', 'SRPT', 'STE', 'STVN', 'SWAV', 'SYK', 'TAK', 'TDOC', 'TECH', 'TEVA', 'TFX', 'THC', 'TMDX', 'TMO', 'UHS', 'UNH', 'UTHR', 'VEEV', 'VRTX', 'VTRS', 'WST', 'ZBH', 'ZTS']

    financials = ['ABR', 'ACGL', 'AFL', 'AGNC', 'AIG', 'AIZ', 'AJG', 'ALL', 'ALLY', 'AMG', 'AON', 'APO', 'ARES', 'ARI', 'AXP', 'BAC', 'BAM', 'BAP', 'BBD', 'BBVA', 'BCH', 'BCS', 'BEN', 'BFH', 'BHF', 'BK', 'BLK', 'BMA', 'BMO', 'BN', 'BNS', 'BPOP', 'BR', 'BRK.A', 'BRK.B', 'BRO', 'BSBR', 'BVN', 'BX', 'BXMT', 'C', 'CACC', 'CB', 'CBOE', 'CBSH', 'CFG', 'CG', 'CIB', 'CINF', 'CM', 'CMA', 'CME', 'CNO', 'COF', 'COOP', 'CPAY', 'CS', 'DB', 'DFS', 'DNB', 'EFX', 'EG', 'ENVA', 'ESNT', 'EVR', 'EWBC', 'FAF', 'FCNCA', 'FDS', 'FG', 'FHN', 'FICO', 'FIS', 'FITB', 'FLT', 'FNB', 'FNF', 'GBCI', 'GGAL', 'GHL', 'GL', 'GPMT', 'GPN', 'GS', 'GWO', 'HBAN', 'HDB', 'HIG', 'HLI', 'HSBC', 'IBKR', 'IBN', 'ICE', 'IFS', 'ING', 'ITUB', 'IVZ', 'JEF', 'JPM', 'KB', 'KEY', 'KKR', 'KNSL', 'L', 'LAZ', 'LNC', 'LPLA', 'LYG', 'MA', 'MC', 'MCO', 'MET', 'MFC', 'MFG', 'MKL', 'MKTX', 'MMC', 'MORN', 'MS', 'MSCI', 'MTB', 'MTG', 'MUFG', 'NAVI', 'NDAQ', 'NLY', 'NMR', 'NU', 'NWG', 'OMF', 'ONB', 'OWL', 'OZK', 'PFSI', 'PGR', 'PJT', 'PMT', 'PNC', 'PNFP', 'PRI', 'PRU', 'PUK', 'RC', 'RDN', 'RF', 'RITM', 'RJF', 'RKT', 'RNR', 'RY', 'SAN', 'SCHW', 'SF', 'SHG', 'SLF', 'SLM', 'SMFG', 'SNV', 'SPGI', 'STC', 'STT', 'STWD', 'SYF', 'TD', 'TFC', 'TROW', 'TRTX', 'TRU', 'TRV', 'TW', 'UBS', 'UBSI', 'UNM', 'USB', 'UWMC', 'V', 'VLY', 'VOYA', 'VRSN', 'WBS', 'WFC', 'WIT', 'WRB', 'WTFC', 'WTW', 'ZION']

    information_technology = ['ACN', 'ADBE', 'ADI', 'ADP', 'AMAT', 'AMD', 'ANET', 'APH', 'APPF', 'ARW', 'ASML', 'ASX', 'AVGO', 'AVT', 'BAH', 'BHE', 'BILL', 'BR', 'CACI', 'CALX', 'CEVA', 'CIEN', 'CLS', 'COHR', 'COMM', 'CRCL', 'CRM', 'CRUS', 'CRWD', 'CSCO', 'CTSH', 'CWAN', 'CYBR', 'DDOG', 'DELL', 'DIOD', 'DOCU', 'DXC', 'EPAM', 'ERIC', 'EXLS', 'FI', 'FIG', 'FLEX', 'FN', 'FTNT', 'G', 'GDDY', 'GFS', 'GIB', 'GLOB', 'GLW', 'GWRE', 'HPE', 'HPQ', 'HUBS', 'IBM', 'INFN', 'INFY', 'INTC', 'INTU', 'IONQ', 'JBL', 'JKHY', 'KEYS', 'KLAC', 'LDOS', 'LITE', 'LRCX', 'LSCC', 'MCHP', 'MDB', 'MKSI', 'MRVL', 'MSI', 'MU', 'NCNO', 'NET', 'NEWR', 'NOK', 'NOW', 'NSIT', 'NTAP', 'NVDA', 'NXPI', 'OKLO', 'OKTA', 'ON', 'ORCL', 'PANW', 'PAYC', 'PAYX', 'PCTY', 'PLTR', 'PLXS', 'PRFT', 'PSTG', 'QCOM', 'QRVO', 'RBLX', 'RGTI', 'RNG', 'RPD', 'S', 'SAIC', 'SANM', 'SAP', 'SCSC', 'SHOP', 'SLAB', 'SMAR', 'SMCI', 'SMTC', 'SNOW', 'SNX', 'SPLK', 'SPOT', 'SQ', 'SSNC', 'STM', 'STX', 'SWKS', 'TASK', 'TDY', 'TEL', 'TENB', 'TSM', 'TTMI', 'TWLO', 'TXN', 'TYL', 'U', 'UI', 'UMC', 'VEEV', 'VIAV', 'VRNS', 'VSH', 'WDAY', 'WDC', 'WIT', 'WIX', 'WOLF', 'XYZ', 'ZM', 'ZS']

    communication_services = ['AMC', 'AMX', 'APPS', 'ATUS', 'BCE', 'BILI', 'CABO', 'CHT', 'CNK', 'CRTO', 'DDL', 'DIS', 'DJCO', 'DKNG', 'EA', 'EDR', 'FLUT', 'FOX', 'FOXA', 'FTR', 'GCI', 'GOOG', 'GOOGL', 'GTN', 'IMAX', 'IPG', 'IQ', 'LEE', 'LUMN', 'LYV', 'META', 'MGID', 'MGNI', 'MSGS', 'NEWM', 'NWS', 'NWSA', 'NXST', 'NYT', 'OMC', 'ORAN', 'PARA', 'PINS', 'PSO', 'PUBM', 'RBLX', 'RCI', 'RDDT', 'SBGI', 'SCHL', 'SCOR', 'SNAP', 'SPOT', 'SSP', 'T', 'TBLA', 'TEF', 'TGNA', 'TKO', 'TLK', 'TME', 'TMUS', 'TTD', 'TTWO', 'TU', 'U', 'USM', 'VIV', 'VOD', 'VZ', 'WBD', 'WMG', 'WPP', 'YELP', 'ZD']

    utilities = ['AEE', 'AEP', 'AES', 'AQN', 'ATO', 'AVA', 'AWK', 'AWR', 'BE', 'BEP', 'BEPC', 'BKH', 'CEG', 'CLNE', 'CMS', 'CNP', 'CPK', 'CWCO', 'CWEN', 'CWT', 'D', 'DTE', 'DUK', 'ED', 'EIX', 'ES', 'ETR', 'EVRG', 'EXC', 'FE', 'FTS', 'GEV', 'IDA', 'LNT', 'MGEE', 'NEE', 'NEP', 'NFG', 'NGG', 'NI', 'NJR', 'NRG', 'NWE', 'NWN', 'OGE', 'OGS', 'ORA', 'OTTR', 'PCG', 'PEG', 'PLUG', 'PNW', 'POR', 'PPL', 'RNW', 'SJW', 'SO', 'SPH', 'SRE', 'SWX', 'UTL', 'VST', 'WEC', 'WTR', 'XEL', 'YORW']

    real_estate = ['ABR', 'ACC', 'ACRE', 'ADC', 'AGNC', 'AHT', 'AIV', 'AKR', 'ALIT', 'AMH', 'AMT', 'APLE', 'APTS', 'ARE', 'ARI', 'ARR', 'AVB', 'BDN', 'BNL', 'BRX', 'BSR', 'BXMT', 'BXP', 'CBL', 'CBRE', 'CCI', 'CHCT', 'CHMI', 'CIO', 'CLDT', 'CLI', 'COMP', 'COR', 'CPT', 'CSGP', 'CTRE', 'CUBE', 'CUZ', 'CWK', 'DEA', 'DEI', 'DLR', 'DOC', 'DRE', 'DRH', 'DX', 'EGP', 'ELME', 'ELS', 'EPR', 'EQC', 'EQIX', 'EQR', 'ESRT', 'ESS', 'EXP', 'EXR', 'FBRT', 'FCPT', 'FPH', 'FR', 'FRT', 'GLPI', 'GMRE', 'GNL', 'GPMT', 'GTY', 'HHH', 'HIW', 'HPP', 'HR', 'HST', 'HT', 'IIPR', 'INVH', 'IRM', 'IRT', 'IVR', 'JBGS', 'JLL', 'KIM', 'KRC', 'KREF', 'KRG', 'LADR', 'LSI', 'LTC', 'LXP', 'MAA', 'MAC', 'MFA', 'MITT', 'MMI', 'MPW', 'NHI', 'NLY', 'NMRK', 'NNN', 'NSA', 'NTST', 'NXR', 'NYMT', 'O', 'OFC', 'OHI', 'OPAD', 'OPEN', 'ORC', 'PDM', 'PEB', 'PEI', 'PGRE', 'PK', 'PLD', 'PLYM', 'PMT', 'PSA', 'QTS', 'RBA', 'RC', 'RDFN', 'REG', 'REXR', 'RHP', 'RITM', 'RLJ', 'ROIC', 'RPAI', 'RWT', 'SAFE', 'SBAC', 'SBRA', 'SHO', 'SITC', 'SKT', 'SLG', 'SPG', 'SRC', 'SRG', 'STAG', 'STOR', 'STWD', 'SUI', 'SVC', 'TRNO', 'TRTX', 'TWO', 'UDR', 'UE', 'UHT', 'VICI', 'VNO', 'VTR', 'WELL', 'WPG', 'WRE', 'XHR']

    stocks = industrials





    # stocks = ['NVDA', 'MSFT', 'AAPL', 'AMZN', 'GOOG', 'GOOGL', 'META', 'AVGO', 'TSLA', 'NFLX', 
    #              'COST', 'PLTR', 'ASML', 'CSCO', 'TMUS', 'AMD', 'LIN', 'AZN', 'INTU', 'TXN', 
    #              'BKNG', 'PEP', 'ISRG', 'QCOM', 'AMAT', 'AMGN', 'ARM', 'ADBE', 'HON', 'PDD', 
    #              'SHOP', 'MU', 'GILD', 'CMCSA', 'LRCX', 'PANW', 'ADP', 'KLAC', 'ADI', 'MSTR', 
    #              'MELI', 'VRTX', 'CRWD', 'SNY', 'APP', 'SBUX', 'INTC', 'DASH', 'CEG', 'CME', 
    #              'IBKR', 'COIN', 'TRI', 'CDNS', 'CTAS', 'MDLZ', 'SNPS', 'HOOD', 'ABNB', 'NTES', 
    #              'ORLY', 'MAR', 'FTNT', 'EQIX', 'PYPL', 'CSX', 'MRVL', 'CHTR', 'CRWV', 'REGN', 
    #              'ADSK', 'WDAY', 'ROP', 'NXPI', 'MNST', 'AXON', 'AEP', 'PAYX', 'NDAQ', 'PCAR', 
    #              'FAST', 'TEAM', 'DDOG', 'CPRT', 'KDP', 'ZS', 'JD', 'EXC', 'CCEP', 'KMB', 
    #              'ROST', 'IDXX', 'TTWO', 'FANG', 'VRSK', 'ALNY', 'TCOM', 'BKR', 'MCHP', 'XEL', 
    #              'FER', 'EA', 'CTSH', 'TTD', 'CSGP', 'EBAY', 'ODFL', 'MPWR', 'GEHC', 'ARGX', 
    #              'ANSS', 'ACGL', 'DXCM', 'TW', 'KHC', 'STX', 'WTW', 'TSCO', 'RYAAY', 'BIDU', 
    #              'LPLA', 'ONC', 'SMCI', 'FITB', 'WBD', 'UAL', 'LULU', 'FCNCA', 'LI', 'BNTX', 
    #              'FCNCO', 'SYM', 'ERIC', 'VOD', 'VRSN', 'FWONK', 'FWONA', 'HBAN', 'EXE', 'ON', 
    #              'FOXA', 'SBAC', 'NTRS', 'FOX', 'SOFI', 'CDW', 'CHKP', 'EXPE', 'PTC', 'WDC', 
    #              'CINF', 'GFS', 'DLTR', 'TROW', 'ZM', 'NTRA', 'ULTA', 'DKNG', 'NTAP', 'CG', 
    #              'FUTU', 'AFRM', 'TPG', 'GRAB', 'ESLT', 'PODD', 'SSNC', 'RPRX', 'STLD', 'BIIB', 
    #              'FLEX', 'NTNX', 'CASY', 'TRMB', 'CYBR', 'Z', 'INSM', 'SMMT', 'ZG', 'PFG', 
    #              'RKLB', 'ERIE', 'GEN', 'BSY', 'NWS', 'FSLR', 'CRDO', 'DUOL', 'FFIV', 'NWSA', 
    #              'ZBRA', 'MDB', 'OKTA', 'LNT', 'DPZ', 'EVRG', 'ARCC', 'ALAB', 'ILMN', 'SFM', 
    #              'RIVN', 'TER', 'KSPI', 'WMG', 'ASTS', 'JBHT', 'COO', 'DOCU', 'EWBC', 'ALGN', 
    #              'HOLX', 'MNDY', 'WWD', 'LOGI', 'LBRDA', 'LBRDK', 'GLPI', 'UTHR', 'GMAB', 'PAA', 
    #              'INCY', 'ENTG', 'NBIX', 'ROKU', 'MRNA', 'MBLY', 'AVAV', 'JKHY', 'LAMR', 'DRS', 
    #              'REG', 'TLN', 'CART', 'NDSN', 'TXRH', 'LECO', 'MORN', 'EXEL', 'ICLR', 'MANH', 
    #              'CHRW', 'CELH', 'HST', 'POOL', 'WYNN', 'SEIC', 'FTAI', 'SWKS', 'AKAM', 'SAIL', 
    #              'BMRN', 'VNOM', 'CHYM', 'LINE', 'VTRS', 'PPC', 'ASND', 'HAS', 'NBIS', 'RGLD', 
    #              'HTHT', 'MTSI', 'WBA', 'LKQ', 'COKE', 'TEM', 'DOX', 'EXAS', 'PCTY', 'NICE', 
    #              'TTAN', 'XP', 'TTEK', 'AGNC', 'SFD', 'COOP', 'CPB', 'MEDP', 'AUR', 'FYBR', 
    #              'WING', 'NXT', 'PNFP', 'PARAA', 'HSIC', 'VRNA', 'FRHC', 'SATS', 'MASI', 'WTFC', 
    #              'BBIO', 'BILI', 'CBSH', 'KTOS', 'DSGX', 'MMYT', 'PARA', 'ONB', 'APPF', 'SRAD', 
    #              'PEGA', 'BZ', 'WIX', 'TECH', 'BPMC', 'UMBF', 'NVMI', 'GRFS', 'VFS', 'ZION', 
    #              'CFLT', 'ENSG', 'QRVO', 'LNW', 'SIRI', 'HLNE', 'HQY', 'MKTX', 'FSV', 'AAL', 
    #              'SAIA', 'MIDD', 'MTCH', 'OLLI', 'BPOP', 'ROIV', 'GLXY', 'CHDN', 'GGAL', 'CORT', 
    #              'DBX', 'OLED', 'LSCC', 'CAI', 'STRL', 'CVLT', 'RGEN', 'RGC', 'APA', 'UPST', 
    #              'OTEX', 'LEGN', 'LLYVK', 'MKSI', 'FIVE', 'LLYVA', 'RVMD', 'HALO', 'CWST', 'STEP', 
    #              'SLM', 'MDGL', 'LCID', 'GTLB', 'RMBS', 'EXLS', 'CIGI', 'ALGM', 'GDS', 'MARA', 
    #              'CAR', 'SNDK', 'JAZZ', 'IONS', 'BOKF', 'BRKR', 'URBN', 'WAY', 'LITE', 'MAT', 
    #              'UFPI', 'TIGO', 'CHRD', 'CCCS', 'LYFT', 'AAON', 'CZR', 'GH', 'IESC', 'ITRI', 
    #              'BULL', 'ETSY', 'OS', 'CACC', 'ROAD', 'FCFS', 'IDCC', 'CROX', 'NUVL', 'OZK', 
    #              'QFIN', 'LFUS', 'CGNX', 'RRR', 'RYTM', 'LNTH', 'GLBE', 'SANM', 'VRNS', 'WSC', 
    #              'MMSI', 'ENPH', 'VERX', 'OMAB', 'NXST', 'TGTX', 'AMKR', 'AXSM', 'CRUS', 'UBSI', 
    #              'VLY', 'AEIS', 'SAIC', 'SITM', 'CHX', 'SIGI', 'FFIN', 'ACT', 'TLX', 'CRSP', 
    #              'COLB', 'GNTX', 'BCPC', 'DJT', 'CHA', 'IEP', 'HWC', 'TSEM', 'CRVL', 'LSTR', 
    #              'SPSC', 'ALKS', 'LIF', 'CALM', 'QLYS', 'OPCH', 'ATAT', 'BGC', 'ESGR', 'LOPE', 
    #              'BWIN', 'ETOR', 'MZTI', 'PECO', 'NOVT', 'AVT', 'SOUN', 'SLAB', 'PCVX', 'PAGP', 
    #              'ACIW', 'REYN', 'FROG', 'PONY', 'SKYW', 'SEZL', 'TTMI', 'SNEX', 'EEFT', 'RIOT', 
    #              'CYTK', 'ADMA', 'SBRA', 'NSIT', 'IPAR', 'VCTR', 'IRTC', 'IBOC', 'SLNO', 'BANF', 
    #              'KRYS', 'GLNG', 'FTDR', 'STNE', 'RUSHB', 'RUSH.A', 'RUSHA', 'WFRD', 'FELE', 'SMTC', 
    #              'RDNT', 'FRSH', 'FIZZ', 'MTSR', 'AKRO', 'CAMT', 'MRUS', 'GBDC', 'SNRE', 'TENB', 
    #              'ODD', 'TCBI', 'VRRM', 'IREN', 'PTCT', 'TMDX', 'ACLX', 'RNA', 'EXPO', 'DORM']

    
    # Run analysis for multiple stocks
    df_results = analyze_multiple_stocks(
        symbols=stocks,
        num_fridays=10,  # Analyze next 3 Fridays
        start_year=2025,
        end_year=2016
    )
    
    # Print results in table format
    print_results_table(df_results)
    
    # Save to CSV
    df_results.to_csv('friday_seasonality_results.csv', index=False)
    print("\nResults saved to 'friday_seasonality_results.csv'")
    
    # Create HTML report with colors
    create_html_report(df_results)