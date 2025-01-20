import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class FTMapGenerator:
    def __init__(self, folder_path,title):
        self.folder_path = folder_path
        if not title:
            raise ValueError("Title is required for FTMap generation")
        self.title = title

    def create_ftmap_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        def create_node(parent, title, origin_id, href=None):
            node = ET.SubElement(parent, "ft:node", {
                "ft:originId": str(origin_id),
                "ft:title": title
            })
            if href:
                node.set("href", href.replace('.md', '.html'))
            return node

        def process_list_items(ul_element, parent_node, origin_counter):
            for li in ul_element.find_all('li', recursive=False):
                a_tag = li.find('a')
                if a_tag:
                    title = a_tag.text.strip()
                    href = a_tag['href']
                    node = create_node(parent_node, title, next(origin_counter), href)
                    nested_ul = li.find('ul')
                    if nested_ul:
                        process_list_items(nested_ul, node, origin_counter)

        root = ET.Element("ft:map", {
            "xmlns:ft": "http://ref.fluidtopics.com/v3/ft#",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:noNamespaceSchemaLocation": "ftmap.xsd",
            "ft:lang": "en-US",
            "ft:title": self.title,
            "ft:originID": "0",
            "ft:editorialType": "book"
        })
        toc = ET.SubElement(root, "ft:toc")
        origin_counter = iter(range(1, 100000))

        # Start processing from the top-level <ul>
        top_ul = soup.find('ul')
        if top_ul:
            process_list_items(top_ul, toc, origin_counter)

        return ET.tostring(root, encoding="unicode")

    def generate(self):
        summary_html_path = os.path.join(self.folder_path, 'SUMMARY.html')
        with open(summary_html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        ftmap_content = self.create_ftmap_from_html(html_content)
        ftmap_path = os.path.join(self.folder_path, 'SUMMARY.ftmap')
        with open(ftmap_path, 'w', encoding='utf-8') as file:
            file.write(ftmap_content)
            
# With h2 tags as the parent.            
# def create_ftmap_from_html(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')

#     def create_node(parent, title, origin_id, href=None):
#         node = ET.SubElement(parent, "ft:node", {
#             "ft:originId": str(origin_id),
#             "ft:title": title
#         })
#         if href:
#             node.set("href", href.replace('.md', '.html'))
#         return node

#     def process_list_items(ul_element, parent_node, origin_counter):
#         for li in ul_element.find_all('li', recursive=False):
#             a_tag = li.find('a')
#             if a_tag:
#                 title = a_tag.text.strip()
#                 href = a_tag['href']
#                 node = create_node(parent_node, title, next(origin_counter), href)
#                 nested_ul = li.find('ul')
#                 if nested_ul:
#                     process_list_items(nested_ul, node, origin_counter)

#     root = ET.Element("ft:map", {
#         "xmlns:ft": "http://ref.fluidtopics.com/v3/ft#",
#         "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
#         "xsi:noNamespaceSchemaLocation": "ftmap.xsd",
#         "ft:lang": "en-US",
#         "ft:title": self.title,
#         "ft:originID": "0",
#         "ft:editorialType": "article"
#     })
#     toc = ET.SubElement(root, "ft:toc")
#     origin_counter = iter(range(1, 100000)) 

#     for h2 in soup.find_all('h2'):
#         current_node = create_node(toc, h2.text.strip(), next(origin_counter))
#         for ul in h2.find_next_siblings('ul', limit=1):
#             process_list_items(ul, current_node, origin_counter)

#     return ET.tostring(root, encoding="unicode")