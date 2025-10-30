import geopandas as gpd

batiments = gpd.read_file("/Users/asmae/Downloads/projet/data/batiments.shp")
infras = gpd.read_file("/Users/asmae/Downloads/projet/data/infrastructures.shp")

print("\n=== CRS CHECK ===")
print("Buildings CRS:", batiments.crs)
print("Infrastructures CRS:", infras.crs)

print("\nFirst building geometry sample:")
print(batiments.geometry.iloc[0])

print("\nFirst infrastructure geometry sample:")
print(infras.geometry.iloc[0])

print("\nBounding boxes:")
print("Buildings extent:", batiments.total_bounds)
print("Infra extent:", infras.total_bounds)
