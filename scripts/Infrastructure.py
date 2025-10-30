"""
Class representing electrical infrastructure (power lines).
"""

class Infrastructure:
    """
    Represents an electrical infrastructure line.
    
    Attributes:
        id_infra (str): Unique identifier for the infrastructure
        type_infra (str): Type of line (aerien, semi-aerien, fourreau)
        geometry: Shapefile geometry object (line)
        length (float): Length of the line in meters
        cost_per_meter (float): Cost per meter based on type
        time_per_meter (float): Installation time per meter
        buildings_connected (list): List of building IDs connected via this line
        shared (bool): Whether this line is shared by multiple buildings
    """
    
    # Cost and time data for different infrastructure types
    INFRASTRUCTURE_SPECS = {
        'aerien': {'cost': 500, 'time': 2},           # €/m, h/m
        'semi-aerien': {'cost': 750, 'time': 4},      # €/m, h/m
        'fourreau': {'cost': 900, 'time': 5}          # €/m, h/m
    }
    
    def __init__(self, id_infra, type_infra, geometry=None):
        """
        Initialize an infrastructure object.
        
        Args:
            id_infra (str): Infrastructure ID
            type_infra (str): Infrastructure type
            geometry: Shapefile geometry (optional)
        """
        self.id_infra = id_infra
        self.type_infra = type_infra
        self.geometry = geometry
        self.length = 0.0
        self.buildings_connected = []
        self.shared = False
        
        # Set cost and time based on type
        specs = self.INFRASTRUCTURE_SPECS.get(type_infra, {'cost': 0, 'time': 0})
        self.cost_per_meter = specs['cost']
        self.time_per_meter = specs['time']
    
    def calculate_length(self):
        """
        Calculate the length of the infrastructure line from geometry.
        
        Returns:
            float: Length in meters
        """
        if self.geometry:
            self.length = self.geometry.length
        return self.length
    
    def get_total_cost(self):
        """
        Calculate total cost for this infrastructure.
        
        Returns:
            float: Total cost in euros
        """
        return self.length * self.cost_per_meter
    
    def get_total_time(self):
        """
        Calculate total installation time for this infrastructure.
        
        Returns:
            float: Total time in hours
        """
        return self.length * self.time_per_meter
    
    def add_building(self, building_id):
        """
        Add a building to the list of buildings connected via this line.
        
        Args:
            building_id (str): Building ID to add
        """
        if building_id not in self.buildings_connected:
            self.buildings_connected.append(building_id)
            if len(self.buildings_connected) > 1:
                self.shared = True
    
    def get_sharing_bonus(self):
        """
        Calculate bonus for line sharing (more buildings = better efficiency).
        
        Returns:
            float: Sharing bonus multiplier
        """
        return len(self.buildings_connected) if self.buildings_connected else 1
    
    def get_cost_per_building(self):
        """
        Calculate cost per building when line is shared.
        
        Returns:
            float: Cost per building
        """
        num_buildings = len(self.buildings_connected)
        if num_buildings > 0:
            return self.get_total_cost() / num_buildings
        return self.get_total_cost()
    
    def __repr__(self):
        return f"Infrastructure({self.id_infra}, {self.type_infra})"
    
    def __str__(self):
        shared_info = f" (shared by {len(self.buildings_connected)} buildings)" if self.shared else ""
        return f"{self.id_infra} ({self.type_infra}): {self.length:.2f}m - {self.get_total_cost():.2f}€{shared_info}"
