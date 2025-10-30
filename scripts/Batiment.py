"""
Class representing a building in the electrical grid network.
"""

class Batiment:
    """
    Represents a building that needs to be connected to the electrical grid.
    
    Attributes:
        id_batiment (str): Unique identifier for the building
        type_batiment (str): Type of building (habitation, école, hôpital)
        nb_maisons (int): Number of houses in the building
        geometry: Shapefile geometry object (point)
        connected (bool): Whether the building is connected to the grid
        connection_cost (float): Cost to connect this building
        connection_time (float): Time to connect this building
        priority_score (float): Calculated priority score for connection
    """
    
    # Priority weights for different building types
    TYPE_PRIORITIES = {
        'hôpital': 100,    # Hospitals have highest priority
        'école': 50,       # Schools have medium priority
        'habitation': 10   # Residential buildings have base priority
    }
    
    def __init__(self, id_batiment, type_batiment, nb_maisons, geometry=None):
        """
        Initialize a building object.
        
        Args:
            id_batiment (str): Building ID
            type_batiment (str): Building type
            nb_maisons (int): Number of houses
            geometry: Shapefile geometry (optional)
        """
        self.id_batiment = id_batiment
        self.type_batiment = type_batiment
        self.nb_maisons = int(nb_maisons)
        self.geometry = geometry
        self.connected = False
        self.connection_cost = 0.0
        self.connection_time = 0.0
        self.priority_score = 0.0
        self.connected_via = None  # Infrastructure used for connection
        
    def calculate_priority(self):
        """
        Calculate priority score based on building type and number of houses.
        Higher score = higher priority for connection.
        
        Returns:
            float: Priority score
        """
        base_priority = self.TYPE_PRIORITIES.get(self.type_batiment, 1)
        # Priority increases with number of houses
        self.priority_score = base_priority * self.nb_maisons
        return self.priority_score
    
    def set_connection_info(self, cost, time, infrastructure_id):
        """
        Set connection information for this building.
        
        Args:
            cost (float): Connection cost in euros
            time (float): Connection time in hours
            infrastructure_id (str): ID of infrastructure used
        """
        self.connection_cost = cost
        self.connection_time = time
        self.connected_via = infrastructure_id
        self.connected = True
    
    def get_efficiency_score(self):
        """
        Calculate efficiency score (houses per euro).
        Higher is better.
        
        Returns:
            float: Efficiency score
        """
        if self.connection_cost > 0:
            return self.nb_maisons / self.connection_cost
        return 0.0
    
    def __repr__(self):
        return f"Batiment({self.id_batiment}, {self.type_batiment}, {self.nb_maisons} maisons)"
    
    def __str__(self):
        status = "Connected" if self.connected else "Not connected"
        return f"{self.id_batiment} ({self.type_batiment}): {self.nb_maisons} maisons - {status}"
