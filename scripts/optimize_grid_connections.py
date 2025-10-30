"""
Optimized electrical grid connection planning with QGIS output.
This script loads building and infrastructure data (from SHAPEFILES ONLY),
calculates optimal connections, and generates shapefiles for QGIS.
"""

import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from Batiment import Batiment
from Infrastructure import Infrastructure


class GridOptimizer:
    """
    Main class for optimizing electrical grid connections.
    """

    def __init__(self):
        self.batiments = {}
        self.infrastructures = {}
        self.connection_plan = []
        self.total_cost = 0.0
        self.total_time = 0.0
        self.buildings_connected = 0
        self.houses_connected = 0
        self.crs = None  # will be set from the buildings shapefile
        self.min_connection_cost = 50.0  # minimum connection cost in euros

    def load_data(self, batiments_csv=None, infrastructures_csv=None,
                  batiments_shp=None, infrastructures_shp=None):
        """
        Load building and infrastructure data from shapefiles (CSV paths can be None).
        """
        print("Loading data...")

        # ------------------------
        # BUILDINGS
        # ------------------------
        if batiments_shp:
            print(f"Reading buildings from shapefile: {batiments_shp}")
            gdf_batiments = gpd.read_file(batiments_shp)
            self.crs = gdf_batiments.crs  # remember CRS for exports
            
            if self.crs and self.crs.is_geographic:
                print(f"⚠️  Buildings are in geographic CRS ({self.crs}), reprojecting to metric (EPSG:3857)...")
                gdf_batiments = gdf_batiments.to_crs("EPSG:3857")
                self.crs = gdf_batiments.crs
                print(f"✓ Reprojected to {self.crs}")

            for idx, row in gdf_batiments.iterrows():
                bat_id = str(
                    row.get('id_batiment')
                    or row.get('ID_BATIMENT')
                    or row.get('id')
                    or idx
                )
                type_b = str(
                    row.get('type_batiment')
                    or row.get('TYPE_BATIMENT')
                    or 'habitation'
                )
                nb_maisons = int(
                    row.get('nb_maisons')
                    or row.get('NB_MAISONS')
                    or 1
                )

                b = Batiment(bat_id, type_b, nb_maisons)
                b.geometry = row.geometry
                b.calculate_priority()
                self.batiments[bat_id] = b

            print(f"Loaded {len(self.batiments)} buildings from shapefile.")
        else:
            raise ValueError("No building shapefile provided.")

        # ------------------------
        # INFRASTRUCTURES
        # ------------------------
        if infrastructures_shp:
            print(f"Reading infrastructures from shapefile: {infrastructures_shp}")
            gdf_infra = gpd.read_file(infrastructures_shp)

            # If infra shapefile has a CRS and we don't, adopt it
            if self.crs is None:
                self.crs = gdf_infra.crs

            if self.crs and gdf_infra.crs and gdf_infra.crs != self.crs:
                print(f"Reprojecting infrastructures from {gdf_infra.crs} to {self.crs}")
                gdf_infra = gdf_infra.to_crs(self.crs)

            for idx, row in gdf_infra.iterrows():
                infra_id = str(
                    row.get('id_infra')
                    or row.get('ID_INFRA')
                    or row.get('id')
                    or idx
                )
                type_i = str(
                    row.get('type_infra')
                    or row.get('TYPE_INFRA')
                    or 'aérien'
                )

                infra = Infrastructure(infra_id, type_i)
                infra.geometry = row.geometry
                infra.calculate_length()
                self.infrastructures[infra_id] = infra

            print(f"Loaded {len(self.infrastructures)} infrastructure lines from shapefile.")
        else:
            raise ValueError("No infrastructure shapefile provided.")
            

    def calculate_connection_costs(self):
        """
        Calculate connection costs for each building based on nearest infrastructure.
        Uses spatial distances if geometries exist; otherwise a fallback estimate.
        """
        print("\nCalculating connection costs...")
        print(f"Using CRS: {self.crs}")
        
        distances = []

        for idx, (bat_id, batiment) in enumerate(self.batiments.items()):
            min_cost = float('inf')
            best_infra = None
            best_time = 0.0
            min_distance = float('inf')

            for infra_id, infra in self.infrastructures.items():
                if infra.geometry is not None and batiment.geometry is not None:
                    # distance from point to line
                    distance = batiment.geometry.distance(infra.geometry)
                    
                    if distance < 1.0:  # Less than 1 meter (or 1 degree if still in geographic coords)
                        distance = 10.0  # Set minimum 10 meter connection distance
                    
                    cost = distance * infra.cost_per_meter
                    time = distance * infra.time_per_meter
                else:
                    # fallback estimate when geometry missing
                    distance = 50.0  # meters
                    cost = distance * infra.cost_per_meter
                    time = distance * infra.time_per_meter

                if cost < min_cost:
                    min_cost = cost
                    best_infra = infra_id
                    best_time = time
                    min_distance = distance

            if best_infra is not None:
                batiment.connection_cost = max(min_cost, self.min_connection_cost)
                batiment.connection_time = best_time
                batiment.connected_via = best_infra
                distances.append(min_distance)

            # Debug print for first few buildings
            if idx < 5:
                print(f"  {bat_id}: nearest infra={best_infra}, distance={min_distance:.2f}m, cost={batiment.connection_cost:.2f}€, time={best_time:.2f}h")

        if distances:
            print(f"\nDistance Statistics:")
            print(f"  Min distance: {min(distances):.2f}m")
            print(f"  Max distance: {max(distances):.2f}m")
            print(f"  Avg distance: {sum(distances)/len(distances):.2f}m")
            print(f"  Buildings with distance < 1m: {sum(1 for d in distances if d < 1.0)}")

    def optimize_connections(self, budget=None, max_time=None):
        """
        Prioritize and select buildings to connect within budget/time constraints.
        Prioritization = hospital > school > house (via priority_score) and cost-efficiency.
        """
        print("\nOptimizing connections...")

        building_scores = []
        for bat_id, b in self.batiments.items():
            if getattr(b, "connection_cost", None):
                efficiency = b.nb_maisons / b.connection_cost
                score = b.priority_score * efficiency
                building_scores.append((score, bat_id, b))

        building_scores.sort(key=lambda x: x[0], reverse=True)
        
        print(f"\nTop 5 connection candidates:")
        for i, (score, bat_id, b) in enumerate(building_scores[:5]):
            print(f"  {i+1}. Building {bat_id}: score={score:.4f}, cost={b.connection_cost:.2f}€, houses={b.nb_maisons}, type={b.type_batiment}")

        cumulative_cost = 0.0
        cumulative_time = 0.0

        for score, bat_id, b in building_scores:
            new_cost = cumulative_cost + b.connection_cost
            new_time = cumulative_time + b.connection_time

            if budget is not None and new_cost > budget:
                continue
            if max_time is not None and new_time > max_time:
                continue

            b.connected = True
            infra = self.infrastructures[b.connected_via]
            infra.add_building(bat_id)

            self.connection_plan.append({
                'building_id': bat_id,
                'building_type': b.type_batiment,
                'nb_houses': b.nb_maisons,
                'infrastructure_id': b.connected_via,
                'infrastructure_type': infra.type_infra,
                'cost': b.connection_cost,
                'time': b.connection_time,
                'priority_score': b.priority_score,
                'efficiency': b.get_efficiency_score()
            })

            cumulative_cost = new_cost
            cumulative_time = new_time
            self.buildings_connected += 1
            self.houses_connected += b.nb_maisons

        self.total_cost = cumulative_cost
        self.total_time = cumulative_time

        print("\nOptimization complete!")
        print(f"Buildings to connect: {self.buildings_connected}/{len(self.batiments)}")
        print(f"Houses to connect: {self.houses_connected}")
        print(f"Total cost: {self.total_cost:,.2f} €")
        print(f"Total time: {self.total_time:,.2f} hours ({self.total_time/24:.1f} days)")
        return self.connection_plan

    def generate_statistics(self):
        """
        Print summary stats for the connection plan.
        """
        print("\n" + "=" * 60)
        print("CONNECTION PLAN STATISTICS")
        print("=" * 60)

        # Building type breakdown
        type_stats = {}
        for item in self.connection_plan:
            btype = item['building_type']
            type_stats.setdefault(btype, {'count': 0, 'houses': 0, 'cost': 0.0})
            type_stats[btype]['count'] += 1
            type_stats[btype]['houses'] += item['nb_houses']
            type_stats[btype]['cost'] += item['cost']

        print("\nBy Building Type:")
        for btype, stats in type_stats.items():
            print(f"  {btype}: {stats['count']} buildings, {stats['houses']} houses, {stats['cost']:,.2f} €")

        if self.buildings_connected:
            print(f"\nAverage cost/building: {self.total_cost / self.buildings_connected:,.2f} €")
        if self.houses_connected:
            print(f"Average cost/house: {self.total_cost / self.houses_connected:,.2f} €")

    def export_to_shapefile(self, output_path):
        """
        Export connected buildings as a shapefile for QGIS.
        """
        print(f"\nExporting buildings to shapefile: {output_path}")

        if not self.connection_plan:
            print("⚠️ No buildings were connected — skipping shapefile export.")
            return

        features = []
        for rank, item in enumerate(self.connection_plan, 1):
            b = self.batiments[item['building_id']]
            geom = b.geometry if b.geometry is not None else Point(0, 0)

            features.append({
                'geometry': geom,
                'id': item['building_id'],
                'type': item['building_type'],
                'nb_maisons': item['nb_houses'],
                'infra_id': item['infrastructure_id'],
                'infra_type': item['infrastructure_type'],
                'cost': round(item['cost'], 2),
                'time_h': round(item['time'], 2),
                'priority': round(item['priority_score'], 2),
                'efficiency': round(item['efficiency'], 6),
                'rank': rank,
                'cost_house': round(item['cost'] / max(item['nb_houses'], 1), 2)
            })

        gdf = gpd.GeoDataFrame(features, geometry=[f["geometry"] for f in features], crs=self.crs or "EPSG:4326")
        gdf.to_file(output_path)
        print("Shapefile exported successfully.")

    def export_connection_lines(self, output_path):
        """
        Export connection lines (building -> nearest point on infra) as a shapefile.
        """
        print(f"\nExporting connection lines to shapefile: {output_path}")

        features = []
        for rank, item in enumerate(self.connection_plan, 1):
            b = self.batiments[item['building_id']]
            infra = self.infrastructures[item['infrastructure_id']]

            if b.geometry is not None and infra.geometry is not None:
                nearest_point = infra.geometry.interpolate(
                    infra.geometry.project(b.geometry)
                )
                line_geom = LineString([b.geometry, nearest_point])

                features.append({
                    'geometry': line_geom,
                    'bat_id': item['building_id'],
                    'bat_type': item['building_type'],
                    'infra_id': item['infrastructure_id'],
                    'infra_type': item['infrastructure_type'],
                    'cost': round(item['cost'], 2),
                    'time_h': round(item['time'], 2),
                    'distance_m': round(line_geom.length, 2),
                    'rank': rank,
                    'nb_maisons': item['nb_houses'],
                    'shared': 1 if getattr(infra, "shared", False) else 0
                })

        if not features:
            print("⚠️ No connection lines with valid geometries to export.")
            return

        gdf = gpd.GeoDataFrame(features, geometry=[f["geometry"] for f in features], crs=self.crs or "EPSG:4326")
        gdf.to_file(output_path)
        print("Connection lines exported successfully.")


def main():
    print("=" * 60)
    print("ELECTRICAL GRID CONNECTION OPTIMIZER")
    print("=" * 60)

    optimizer = GridOptimizer()

    optimizer.load_data(
        batiments_csv=None,
        infrastructures_csv=None,
        batiments_shp='/Users/asmae/Downloads/projet/data/batiments.shp',
        infrastructures_shp='/Users/asmae/Downloads/projet/data/infrastructures.shp'
    )

    optimizer.calculate_connection_costs()
    optimizer.optimize_connections(budget=1_000_000)
    optimizer.generate_statistics()

    optimizer.export_to_shapefile('optimal_solution_buildings_connected.shp')
    optimizer.export_connection_lines('optimal_solution_connection_lines.shp')

    # CSV + JSON summaries
    pd.DataFrame(optimizer.connection_plan).to_csv('optimal_solution_summary.csv', index=False)
    stats = {
        'total_buildings_connected': optimizer.buildings_connected,
        'total_buildings': len(optimizer.batiments),
        'total_houses_connected': optimizer.houses_connected,
        'total_cost_euros': round(optimizer.total_cost, 2),
        'total_time_hours': round(optimizer.total_time, 2),
        'total_time_days': round(optimizer.total_time / 24, 1),
        'avg_cost_per_building': round(optimizer.total_cost / max(optimizer.buildings_connected, 1), 2),
        'avg_cost_per_house': round(optimizer.total_cost / max(optimizer.houses_connected, 1), 2),
        'efficiency_houses_per_1000_euros': round(
            optimizer.houses_connected / max(optimizer.total_cost / 1000, 1e-9), 2
        )
    }
    with open('optimal_solution_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)

    print("\n" + "=" * 60)
    print("OPTIMIZATION COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. optimal_solution_buildings_connected.shp")
    print("  2. optimal_solution_connection_lines.shp")
    print("  3. optimal_solution_summary.csv")
    print("  4. optimal_solution_statistics.json")


if __name__ == "__main__":
    main()
