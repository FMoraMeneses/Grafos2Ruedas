import xml.etree.ElementTree as ET

# Ruta al archivo original
input_file = "../map.osm"
# Archivo de salida limpio
output_file = "map_clean.osm"

# Cargar el XML
tree = ET.parse(input_file)
root = tree.getroot()

# Atributos a eliminar
attrs_to_remove = {"visible", "version", "user", "uid", "changeset", "timestamp"}

# Recorrer todos los nodos del tipo <node>
for node in root.findall("node"):
    for attr in attrs_to_remove:
        if attr in node.attrib:
            del node.attrib[attr]

attrs_to_remove = {"visible", "version", "user", "uid", "changeset"}

for node in root.findall("relation"):
    for attr in attrs_to_remove:
        if attr in node.attrib:
            del node.attrib[attr]

attrs_to_remove = {"visible", "version", "user", "uid", "changeset"}

for node in root.findall("way"):
    for attr in attrs_to_remove:
        if attr in node.attrib:
            del node.attrib[attr]


# Guardar el nuevo archivo
tree.write(output_file, encoding="utf-8", xml_declaration=True)

print(f"✅ Archivo limpiado guardado como '{output_file}'")
