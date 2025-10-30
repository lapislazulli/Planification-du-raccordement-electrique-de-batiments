"""
Generate QGIS style files (.qml) for automatic styling of the solution layers
"""

def create_buildings_style():
    """Create QML style for buildings layer with color coding by priority"""
    qml_content = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0">
  <renderer-v2 type="categorizedSymbol" attr="type" forceraster="0">
    <categories>
      <category render="true" symbol="0" value="hôpital" label="Hospital (Critical)"/>
      <category render="true" symbol="1" value="école" label="School (High Priority)"/>
      <category render="true" symbol="2" value="habitation" label="Residential"/>
    </categories>
    <symbols>
      <symbol type="marker" name="0" alpha="1">
        <layer class="SimpleMarker">
          <prop k="color" v="255,0,0,255"/>
          <prop k="size" v="5"/>
          <prop k="outline_color" v="128,0,0,255"/>
          <prop k="outline_width" v="0.5"/>
        </layer>
      </symbol>
      <symbol type="marker" name="1" alpha="1">
        <layer class="SimpleMarker">
          <prop k="color" v="255,165,0,255"/>
          <prop k="size" v="4"/>
          <prop k="outline_color" v="128,82,0,255"/>
          <prop k="outline_width" v="0.5"/>
        </layer>
      </symbol>
      <symbol type="marker" name="2" alpha="1">
        <layer class="SimpleMarker">
          <prop k="color" v="0,128,255,255"/>
          <prop k="size" v="3"/>
          <prop k="outline_color" v="0,64,128,255"/>
          <prop k="outline_width" v="0.5"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontFamily="Arial" fontSize="8" textColor="0,0,0,255">
        <text-buffer bufferDraw="1" bufferSize="1" bufferColor="255,255,255,255"/>
      </text-style>
      <placement placement="1" dist="2"/>
      <rendering displayAll="0" obstacle="1"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
    </settings>
  </labeling>
</qgis>"""
    
    with open('optimal_solution_buildings_connected.qml', 'w') as f:
        f.write(qml_content)
    print("✓ Created buildings style file: optimal_solution_buildings_connected.qml")

def create_lines_style():
    """Create QML style for connection lines with graduated colors by cost"""
    qml_content = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0">
  <renderer-v2 type="categorizedSymbol" attr="infra_type" forceraster="0">
    <categories>
      <category render="true" symbol="0" value="aerien" label="Aerial (500€/m)"/>
      <category render="true" symbol="1" value="semi-aerien" label="Semi-Aerial (750€/m)"/>
      <category render="true" symbol="2" value="fourreau" label="Underground (900€/m)"/>
    </categories>
    <symbols>
      <symbol type="line" name="0" alpha="1">
        <layer class="SimpleLine">
          <prop k="line_color" v="0,255,0,255"/>
          <prop k="line_width" v="1.5"/>
          <prop k="line_style" v="solid"/>
        </layer>
      </symbol>
      <symbol type="line" name="1" alpha="1">
        <layer class="SimpleLine">
          <prop k="line_color" v="255,165,0,255"/>
          <prop k="line_width" v="1.5"/>
          <prop k="line_style" v="dash"/>
        </layer>
      </symbol>
      <symbol type="line" name="2" alpha="1">
        <layer class="SimpleLine">
          <prop k="line_color" v="255,0,0,255"/>
          <prop k="line_width" v="2"/>
          <prop k="line_style" v="solid"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style fontFamily="Arial" fontSize="7" textColor="0,0,0,255">
        <text-buffer bufferDraw="1" bufferSize="0.8" bufferColor="255,255,255,200"/>
      </text-style>
      <placement placement="2" dist="1"/>
      <rendering displayAll="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
    </settings>
  </labeling>
</qgis>"""
    
    with open('optimal_solution_connection_lines.qml', 'w') as f:
        f.write(qml_content)
    print("✓ Created connection lines style file: optimal_solution_connection_lines.qml")

def main():
    """Generate all QGIS style files"""
    print("Generating QGIS style files...")
    create_buildings_style()
    create_lines_style()
    print("\n✅ Style files created! Place them in the same folder as your shapefiles.")
    print("QGIS will automatically apply these styles when you load the layers.")

if __name__ == "__main__":
    main()
