from os import system
import xml.etree.ElementTree as ET
import xml.dom.minidom

system("iccToXml LEN160_3_2K_cal.icm c.xml")


def modify_xml(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the Tags element
    tags = root.find(".//Tags")
    if tags is None:
        print("Error: Tags element not found in the XML file.")
        return

    # Remove specific textType element
    for textType in tags.findall(".//textType"):
        if (
            textType.find("TagSignature").text == "DDPS"
            and textType.find("ASCII").text is None
        ):
            tags.remove(textType)

    # Remove all curveType elements
    for curveType in tags.findall(".//curveType"):
        tags.remove(curveType)

    # Create new elements
    chad_element = ET.Element("s15Fixed16ArrayType")
    ET.SubElement(chad_element, "TagSignature").text = "chad"
    array_element = ET.SubElement(chad_element, "Array")
    array_element.text = "\n            1.04788208 0.02291870 -0.05021667\n            0.02958679 0.99047852 -0.01707458\n            -0.00924683 0.01507568 0.75167847\n      "

    parametricCurveType = ET.Element("parametricCurveType")
    ET.SubElement(parametricCurveType, "TagSignature").text = "rTRC"
    ET.SubElement(parametricCurveType, "TagSignature").text = "gTRC"
    ET.SubElement(parametricCurveType, "TagSignature").text = "bTRC"
    parametricCurve = ET.SubElement(
        parametricCurveType, "ParametricCurve", FunctionType="0"
    )
    parametricCurve.text = "\n        2.46\n      "

    # Update XYZType elements
    xyz_data = [
        ("rXYZ", "0.67344666", "0.27902222", "-0.00193787"),
        ("gXYZ", "0.16564941", "0.67535400", "0.02998352"),
        ("bXYZ", "0.12504578", "0.04560852", "0.79689026"),
    ]

    for tag, x, y, z in xyz_data:
        xyzType = tags.find(f".//XYZType[TagSignature='{tag}']")
        if xyzType is None:
            xyzType = ET.Element("XYZType")
            ET.SubElement(xyzType, "TagSignature").text = tag
            tags.append(xyzType)
        xyzNumber = xyzType.find("XYZNumber")
        if xyzNumber is None:
            xyzNumber = ET.SubElement(xyzType, "XYZNumber")
        xyzNumber.set("X", x)
        xyzNumber.set("Y", y)
        xyzNumber.set("Z", z)

    # Reorder elements
    desired_order = [
        "textDescriptionType",
        "s15Fixed16ArrayType",
        "textType",
        "XYZType",
        "XYZType",
        "XYZType",
        "XYZType",
        "XYZType",
        "parametricCurveType",
        "PrivateType",
        "PrivateType",
        "dictType",
    ]
    new_tags = ET.Element("Tags")

    for tag in desired_order:
        if tag == "s15Fixed16ArrayType":
            new_tags.append(chad_element)
        elif tag == "parametricCurveType":
            new_tags.append(parametricCurveType)
        else:
            elements = tags.findall(f".//{tag}")
            for elem in elements:
                new_tags.append(elem)

    root.remove(tags)
    root.append(new_tags)

    # Write the modified XML back to the file
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)

    # Pretty print the XML
    dom = xml.dom.minidom.parse(xml_file)
    pretty_xml = dom.toprettyxml(indent="  ")
    with open(xml_file, "w") as f:
        f.write(pretty_xml)


# Use the function
modify_xml("c.xml")
print("The XML file has been modified according to the specifications.")


def replace_filename_in_xml(input_file, output_file):
    with open(input_file, "r") as file:
        content = file.read()
    modified_content = content.replace(
        "LEN160_3_2K_cal.icm", "LEN160_3_2K_cal-linux.icc"
    )
    with open(output_file, "w") as file:
        file.write(modified_content)


# Usage
input_xml = output_xml = "c.xml"
replace_filename_in_xml(input_xml, output_xml)
print(f"File has been modified and saved as {output_xml}")

system("iccFromXml c.xml /output/LEN160_3_2K_cal-linux.icc")
