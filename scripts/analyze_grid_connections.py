"""
Electrical Grid Connection Planning Script
Analyzes building connections to optimize cost and maximize connections
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import json

def load_network_data(filepath='reseau_en_arbre.xlsx'):
    """Load the network tree data from Excel file"""
    try:
        df = pd.read_excel(filepath)
        print(f"✓ Loaded {len(df)} connections from network data")
        print(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def build_graph(df):
    """
    Build a graph representation of the network
    Returns: dict with node connections and costs
    """
    graph = defaultdict(list)
    costs = {}
    
    # Assuming columns like: source, target, cost, nb_prises (number of connections)
    for idx, row in df.iterrows():
        # Adapt column names based on actual data structure
        source = row.get('source', row.get('from', idx))
        target = row.get('target', row.get('to', idx + 1))
        cost = row.get('cost', row.get('cout', 0))
        nb_connections = row.get('nb_prises', row.get('prises', 1))
        
        # Build bidirectional graph
        graph[source].append({
            'target': target,
            'cost': cost,
            'connections': nb_connections
        })
        
        costs[(source, target)] = {
            'cost': cost,
            'connections': nb_connections
        }
    
    return graph, costs

def calculate_priority_metric(cost, nb_connections, shared_lines=0):
    """
    Calculate priority metric for building connection
    
    Priority = (Number of connections / Cost) * (1 + Sharing bonus)
    
    Higher value = Higher priority (more connections per euro, with bonus for sharing)
    """
    if cost == 0:
        return float('inf')
    
    # Base metric: connections per unit cost
    base_metric = nb_connections / cost
    
    # Bonus for line sharing (reduces effective cost)
    sharing_bonus = 0.2 * shared_lines  # 20% bonus per shared line
    
    priority = base_metric * (1 + sharing_bonus)
    
    return priority

def analyze_connections(graph, costs):
    """
    Analyze all connections and calculate priorities
    """
    connection_analysis = []
    
    for (source, target), info in costs.items():
        cost = info['cost']
        connections = info['connections']
        
        # Calculate priority metric
        priority = calculate_priority_metric(cost, connections)
        
        # Calculate cost per connection
        cost_per_connection = cost / connections if connections > 0 else float('inf')
        
        connection_analysis.append({
            'source': source,
            'target': target,
            'cost': cost,
            'connections': connections,
            'cost_per_connection': cost_per_connection,
            'priority_score': priority
        })
    
    # Sort by priority (highest first)
    connection_analysis.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return connection_analysis

def create_connection_plan(connection_analysis, budget=None):
    """
    Create an optimized connection plan
    
    Strategy:
    1. Sort by priority score
    2. Select connections that maximize connections/cost ratio
    3. Consider line sharing opportunities
    """
    plan = []
    total_cost = 0
    total_connections = 0
    connected_buildings = set()
    
    print("\n" + "="*70)
    print("CONNECTION PLAN - Prioritized by Cost Efficiency")
    print("="*70)
    
    for idx, conn in enumerate(connection_analysis, 1):
        # Check budget constraint if specified
        if budget and (total_cost + conn['cost']) > budget:
            print(f"\n⚠ Budget limit reached at connection #{idx}")
            break
        
        # Add to plan
        plan.append(conn)
        total_cost += conn['cost']
        total_connections += conn['connections']
        connected_buildings.add(conn['source'])
        connected_buildings.add(conn['target'])
        
        # Print connection details
        print(f"\n#{idx}. Connect {conn['source']} → {conn['target']}")
        print(f"   Cost: €{conn['cost']:,.2f}")
        print(f"   Connections: {conn['connections']}")
        print(f"   Cost/Connection: €{conn['cost_per_connection']:,.2f}")
        print(f"   Priority Score: {conn['priority_score']:.4f}")
        print(f"   Running Total: €{total_cost:,.2f} | {total_connections} connections")
    
    return plan, total_cost, total_connections, connected_buildings

def generate_summary_statistics(plan, total_cost, total_connections, connected_buildings):
    """Generate summary statistics for the connection plan"""
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(f"Total Connections Made: {len(plan)}")
    print(f"Total Cost: €{total_cost:,.2f}")
    print(f"Total Buildings Connected: {len(connected_buildings)}")
    print(f"Total Electrical Connections: {total_connections}")
    print(f"Average Cost per Connection: €{total_cost/total_connections:,.2f}")
    print(f"Average Connections per Building Link: {total_connections/len(plan):.2f}")
    
    # Calculate efficiency metrics
    if plan:
        best_connection = max(plan, key=lambda x: x['priority_score'])
        worst_connection = min(plan, key=lambda x: x['priority_score'])
        
        print(f"\nMost Efficient Connection:")
        print(f"  {best_connection['source']} → {best_connection['target']}")
        print(f"  Priority Score: {best_connection['priority_score']:.4f}")
        
        print(f"\nLeast Efficient Connection (still included):")
        print(f"  {worst_connection['source']} → {worst_connection['target']}")
        print(f"  Priority Score: {worst_connection['priority_score']:.4f}")

def identify_sharing_opportunities(graph, plan):
    """
    Identify opportunities for line sharing to reduce costs
    """
    print("\n" + "="*70)
    print("LINE SHARING OPPORTUNITIES")
    print("="*70)
    
    # Track which nodes are connected
    connected_nodes = set()
    for conn in plan:
        connected_nodes.add(conn['source'])
        connected_nodes.add(conn['target'])
    
    # Find potential shared infrastructure
    sharing_opportunities = []
    node_connections = defaultdict(list)
    
    for conn in plan:
        node_connections[conn['source']].append(conn)
        node_connections[conn['target']].append(conn)
    
    # Nodes with multiple connections can share infrastructure
    for node, connections in node_connections.items():
        if len(connections) > 1:
            total_shared_cost = sum(c['cost'] for c in connections)
            total_shared_connections = sum(c['connections'] for c in connections)
            sharing_opportunities.append({
                'node': node,
                'num_shared_lines': len(connections),
                'total_cost': total_shared_cost,
                'total_connections': total_shared_connections,
                'potential_savings': total_shared_cost * 0.15  # Assume 15% savings from sharing
            })
    
    if sharing_opportunities:
        sharing_opportunities.sort(key=lambda x: x['potential_savings'], reverse=True)
        print(f"\nFound {len(sharing_opportunities)} nodes with sharing potential:")
        for opp in sharing_opportunities[:5]:  # Show top 5
            print(f"\n  Node {opp['node']}:")
            print(f"    Shared lines: {opp['num_shared_lines']}")
            print(f"    Total connections: {opp['total_connections']}")
            print(f"    Potential savings: €{opp['potential_savings']:,.2f}")
    else:
        print("\nNo significant sharing opportunities identified in current plan.")

def main():
    """Main execution function"""
    print("="*70)
    print("ELECTRICAL GRID CONNECTION PLANNING ANALYSIS")
    print("="*70)
    
    # Load data
    df = load_network_data()
    if df is None:
        print("Failed to load data. Exiting.")
        return
    
    # Build graph
    print("\nBuilding network graph...")
    graph, costs = build_graph(df)
    print(f"✓ Graph built with {len(costs)} connections")
    
    # Analyze connections
    print("\nAnalyzing connection priorities...")
    connection_analysis = analyze_connections(graph, costs)
    
    # Create connection plan
    plan, total_cost, total_connections, connected_buildings = create_connection_plan(
        connection_analysis,
        budget=None  # Set budget limit if needed, e.g., budget=100000
    )
    
    # Generate summary
    generate_summary_statistics(plan, total_cost, total_connections, connected_buildings)
    
    # Identify sharing opportunities
    identify_sharing_opportunities(graph, plan)
    
    # Export results
    print("\n" + "="*70)
    print("Exporting results...")
    results_df = pd.DataFrame(plan)
    results_df.to_csv('connection_plan.csv', index=False)
    print("✓ Results exported to 'connection_plan.csv'")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
