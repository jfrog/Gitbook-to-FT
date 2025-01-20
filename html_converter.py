import os
import re
import logging
import mistune
from bs4 import BeautifulSoup
import html

logger = logging.getLogger(__name__)

class MyRenderer(mistune.HTMLRenderer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hint_stack = []

    def list_item(self, text):
        return f'<li><p>{text}</p></li>'

    def table_cell(self, content, **flags):
        tag = 'td' if not flags.get('header', False) else 'th'
        align = flags.get('align', None)
        if align:
            return f'<{tag} style="text-align: {align}"><p>{content}</p></{tag}>'
        return f'<{tag}><p>{content}</p></{tag}>'

    def block_html(self, html):
        hint_start = re.match(r'{%\s*hint\s+style="(\w+)"\s*%}', html)
        if hint_start:
            self.hint_stack.append(hint_start.group(1))
            return f'<div class="{hint_start.group(1)}">'
        elif html.strip() == '{% endhint %}' and self.hint_stack:
            self.hint_stack.pop()
            return '</div>'
        return super().block_html(html)

    def paragraph(self, text):
        if self.hint_stack:
            return f'<p>{text}</p>'
        return super().paragraph(text)

    def render(self, tokens, state):
        output = []
        for tok in tokens:
            if tok['type'] == 'block_html':
                output.append(self.block_html(tok['text']))
            else:
                output.append(super().render([tok], state))
        return ''.join(output)

class HTMLConverter:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def correct_markdown_tables(self, markdown_content):
        lines = markdown_content.split('\n')
        corrected_lines = []
        in_table = False
        header_columns = 0

        for line in lines:
            if '|' in line:
                column_count = line.count('|')

                if '---' in line and not in_table:
                    header_columns = column_count
                    in_table = True
                    if corrected_lines and corrected_lines[-1].count('|') != header_columns:
                        parts = corrected_lines[-1].split('|')
                        if len(parts) - 1 < header_columns:
                            corrected_lines[-1] += '|' * (header_columns - len(parts) + 1)
                elif in_table:
                    parts = line.split('|')
                    if len(parts) - 1 < header_columns:
                        line += '|' * (header_columns - len(parts) + 1)
                    elif len(parts) - 1 > header_columns:
                        line = '|'.join(parts[:header_columns + 1])
                
                corrected_lines.append(line)
            else:
                if in_table:
                    in_table = False
                corrected_lines.append(line)

        return '\n'.join(corrected_lines)

    def convert_markdown_to_html(self, markdown_file_path):
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_text = file.read()

        # Clean up the Markdown
        markdown_text = re.sub(r'\n\\$', '', markdown_text, flags=re.MULTILINE)  # Remove trailing backslashes
        markdown_text = re.sub(r'\n\s*\n', '\n\n', markdown_text)  # Remove multiple empty lines

        # Replace hint blocks before Markdown conversion
        markdown_text = re.sub(r'{%\s*hint\s+style="(\w+)"\s*%}', r'<div class="note"><h3 class="title">Note</h3>', markdown_text)
        markdown_text = re.sub(r'{%\s*endhint\s*%}', '</div>', markdown_text)

        # Unescape HTML entities in the markdown text
        markdown_text = html.unescape(markdown_text)

        corrected_markdown = self.correct_markdown_tables(markdown_text)
        renderer = MyRenderer(escape=False)
        markdown = mistune.create_markdown(renderer=renderer, plugins=['table'])
        html_content = markdown(corrected_markdown)
        
        # Post-process HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove <p> tags wrapping hint blocks
        for div in soup.find_all('div', class_=True):
            if div.parent and div.parent.name == 'p':
                div.parent.replace_with(div)
        
        # Handle pre and code tags
        self.process_pre_tags(soup)
        self.process_code_tags(soup)

        # Remove empty paragraphs
        for p in soup.find_all('p'):
            if not p.contents or (len(p.contents) == 1 and isinstance(p.contents[0], str) and not p.contents[0].strip()):
                p.decompose()

        return str(soup)

    def process_pre_tags(self, soup):
        for pre in soup.find_all('pre'):
            # Add 'programlisting' class to all pre tags
            if 'class' in pre.attrs:
                if isinstance(pre['class'], list):
                    if 'programlisting' not in pre['class']:
                        pre['class'].append('programlisting')
                else:
                    pre['class'] = [pre['class'], 'programlisting']
            else:
                pre['class'] = ['programlisting']
            
            # If there's a code tag inside pre, keep its content but remove the tag
            code = pre.find('code')
            if code:
                code_content = code.encode_contents()  # This preserves inner HTML
                code.unwrap()
                pre.clear()
                pre.append(BeautifulSoup(code_content, 'html.parser'))

    def process_code_tags(self, soup):
        for code in soup.find_all('code'):
            # Add 'code' class to all code tags
            if 'class' in code.attrs:
                if isinstance(code['class'], list):
                    if 'code' not in code['class']:
                        code['class'].append('code')
                else:
                    code['class'] = [code['class'], 'code']
            else:
                code['class'] = ['code']

    def manipulate_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        first_element = soup.find()
        if first_element and first_element.name == 'h1':
            first_element.decompose()

        for thead in soup.find_all('thead'):
            if not thead.get_text(strip=True):
                thead.decompose()

        self.remove_empty_columns(soup)
        self.process_table_cells(soup)
        self.convert_td_to_th(soup)
        self.add_table_border(soup)

        # Unescape HTML entities in all text nodes
        for text in soup.find_all(text=True):
            unescaped_text = html.unescape(text.string)
            text.replace_with(unescaped_text)

        return str(soup)

    def remove_empty_columns(self, soup):
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if not rows:
                continue

            num_cols = len(rows[0].find_all(['th', 'td']))
            empty_cols = [True] * num_cols

            for row in rows:
                columns = row.find_all(['th', 'td'])
                for index, column in enumerate(columns):
                    if column.get_text(strip=True):
                        empty_cols[index] = False

            if any(empty_cols):
                for row in rows:
                    columns = row.find_all(['th', 'td'])
                    for index, is_empty in reversed(list(enumerate(empty_cols))):
                        if is_empty and index < len(columns):
                            columns[index].decompose()

    def process_table_cells(self, soup):
        for cell in soup.find_all(['td', 'th']):
            if cell.contents:
                if not cell.find():
                    text = cell.text.strip()
                    if text:
                        cell.string = ''
                        new_p = soup.new_tag('p')
                        new_p.string = text
                        cell.append(new_p)
            else:
                cell.clear()
            
            # Convert code and pre tags to p tags inside td and th
            for tag in cell.find_all(['code', 'pre']):
                p = soup.new_tag('p')
                if tag.string:
                    p.string = tag.string
                else:
                    p.extend(tag.contents)
                tag.replace_with(p)

    def convert_td_to_th(self, soup):
        for thead in soup.find_all('thead'):
            for tr in thead.find_all('tr'):
                for td in tr.find_all('td'):
                    th = soup.new_tag('th')
                    th.attrs = td.attrs
                    th.string = td.string
                    td.replace_with(th)

    def add_table_border(self, soup):
        for table in soup.find_all('table'):
            if table.find('thead'):
                table['style'] = table.get('style', '') + ' border-top: 0.5px solid #000000 !important;'

    def convert_all(self):
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.md'):
                    md_path = os.path.join(root, file)
                    html_content = self.convert_markdown_to_html(md_path)
                    manipulated_html = self.manipulate_html(html_content)
                    html_path = os.path.splitext(md_path)[0] + '.html'
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(manipulated_html)
                    os.remove(md_path)
                    logger.info(f"Converted and manipulated: {md_path} to {html_path}")