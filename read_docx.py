import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def extract_text_from_docx(docx_path):
    try:
        document_text = ""
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.XML(xml_content)
            
            # XML namespaces used in docx
            WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            PARA = WORD_NAMESPACE + 'p'
            TEXT = WORD_NAMESPACE + 't'
            
            for paragraph in tree.iter(PARA):
                texts = [node.text
                         for node in paragraph.iter(TEXT)
                         if node.text]
                if texts:
                    document_text += ''.join(texts) + "\n"
        return document_text
    except Exception as e:
        return f"Error reading {docx_path}: {e}"

docs = [
    "BHATTARAI_ROYAL_MR_NP069621_NP3F2509IT_CE_IR.docx",
    "DENIS_KUMAR_THAPA_NP069454_CORE_FYP (1).docx"
]

for doc in docs:
    path = os.path.join(r"c:\Users\NITOR 5\Desktop\FYP", doc)
    text = extract_text_from_docx(path)
    output_path = path + ".txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Wrote {output_path}")
