import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import yaml
import pdb


def create_xml_node(ft_publication_title, title, href, children=None):
    node = ET.Element("ft:node", {"ft:title": title, "href": href})

    # Create ft:metas
    ft_metas = ET.SubElement(node, "ft:metas")
    
    # Create ft:meta with pretty URL
    safe_ft_publication_title = ft_publication_title.replace(" ", "-").lower()
    safe_href = href[:-3].replace(" ", "-").replace("README","").lower()  # Also replace spaces in href if needed
    pretty_url = f"{safe_ft_publication_title}/{safe_href}"
    ET.SubElement(ft_metas, "ft:meta", key="topicUrl").text = pretty_url

    if children:
        for child in children:
            node.append(child)
    return node

def parse_lines(ft_publication_title, lines, level=0):
    nodes = []
    while lines:
        line = lines[0]
        if '*' not in line:
            lines.pop(0)
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent < level:
            break
        lines.pop(0)
        parts = line.strip().split("](")
        title = parts[0].lstrip("* [")
        href = parts[1].rstrip(")")
        children = parse_lines(ft_publication_title, lines, level + 2)
        nodes.append(create_xml_node(ft_publication_title, title, href, children))
    return nodes

def convert_to_xml(lines, ft_publication_title):
    root_node = ET.Element("ft:map", {"xmlns:ft": "http://ref.fluidtopics.com/v3/ft#",
                                      "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                      "xsi:noNamespaceSchemaLocation": "ftmap.xsd",
                                        "ft:lang": "en-US",
                                        "ft:title": ft_publication_title,
                                        "ft:originID": "0",
                                        "ft:editorialType": "book"})
    toc_node = ET.Element("ft:toc")
    root_node.append(toc_node)
    xml_nodes = parse_lines(ft_publication_title,lines)
    for node in xml_nodes:
        toc_node.append(node)
    return ET.ElementTree(root_node)


def pretty_print_xml(tree):
    xml_str = ET.tostring(tree.getroot(), encoding='utf-8')
    parsed_str = minidom.parseString(xml_str)
    return "\n".join(parsed_str.toprettyxml(indent="\t").split("\n")[1:])

def add_metadata(xml_tree, metadata):
    # Iterate over nodes and update metadata
    for element in xml_tree.iter():
        if not element.tag.endswith("node"):
            continue
        node = element
        href = node.get("href")
        if href in metadata:
            metas_elem = node.find("ft:metas")
            if metas_elem is None:
                metas_elem = ET.SubElement(node, "ft:metas")

            for key, value in metadata[href].items():
                meta_elem = ET.SubElement(metas_elem, "ft:meta")
                meta_elem.set("key", key)
                meta_elem.text = value

def create_summary(input_folder, output_folder, ft_publication_title):
    """
    Creates a summary file for the converted content.
    """
    # Read the original summary file
    with open(input_folder + "/SUMMARY.md", "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Convert the summary file to Fluid Topics format
    xml_tree = convert_to_xml(lines, ft_publication_title)

    # add metadata
    with open(input_folder + "/metadata.yaml", "r") as file:
        metadata = yaml.safe_load(file).get("metadata", {})
        add_metadata(xml_tree, metadata)

    # buitify the xml
    pretty_xml = pretty_print_xml(xml_tree)

    # Save the summary file in the output folder
    with open(output_folder + "/Summary.ftmap", "w", encoding="utf-8") as file:
        file.write(pretty_xml)
