import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_plots():
    """Creates plots from the processed data and saves them."""
    
    try:
        # Load the processed data
        df = pd.read_csv("../data/processed/merged_data.csv")
        
        print("Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create a figure with multiple subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Airline Performance Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Satisfaction Score by Airline
        bars = ax1.bar(df['Airline'], df['Avg_Satisfaction_Score'] * 100, color='lightcoral')
        ax1.set_title('Customer Satisfaction Score by Airline')
        ax1.set_ylabel('Satisfaction Score (%)')
        ax1.tick_params(axis='x', rotation=45)
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Plot 2: Average Arrival Delay by Airline
        bars = ax2.bar(df['Airline'], df['Avg_Arrival_Delay'], color='lightblue')
        ax2.set_title('Average Arrival Delay by Airline')
        ax2.set_ylabel('Delay (Minutes)')
        ax2.tick_params(axis='x', rotation=45)
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}m', ha='center', va='bottom')
        
        # Plot 3: Satisfaction vs Arrival Delay Scatter
        scatter = ax3.scatter(df['Avg_Arrival_Delay'], df['Avg_Satisfaction_Score'] * 100, 
                             s=df['Total_Surveys']/10, alpha=0.7, c=range(len(df)), cmap='viridis')
        ax3.set_title('Satisfaction vs Arrival Delay')
        ax3.set_xlabel('Average Arrival Delay (Minutes)')
        ax3.set_ylabel('Satisfaction Score (%)')
        # Add airline labels
        for i, airline in enumerate(df['Airline']):
            ax3.annotate(airline, (df['Avg_Arrival_Delay'].iloc[i], df['Avg_Satisfaction_Score'].iloc[i] * 100),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Plot 4: Cancellation Rate by Airline
        bars = ax4.bar(df['Airline'], df['Cancellation_Rate'] * 100, color='lightgreen')
        ax4.set_title('Cancellation Rate by Airline')
        ax4.set_ylabel('Cancellation Rate (%)')
        ax4.tick_params(axis='x', rotation=45)
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save the plot
        plots_dir = "../reports/figures"
        os.makedirs(plots_dir, exist_ok=True)
        plt.savefig(f"{plots_dir}/airline_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Plot saved to reports/figures/airline_analysis.png")
        
        # Create a correlation heatmap
        plt.figure(figsize=(10, 8))
        numeric_df = df.select_dtypes(include=['number'])
        correlation_matrix = numeric_df.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Matrix of Airline Metrics')
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/correlation_heatmap.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Correlation heatmap saved to reports/figures/correlation_heatmap.png")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        raise

if __name__ == "__main__":
    create_plots()