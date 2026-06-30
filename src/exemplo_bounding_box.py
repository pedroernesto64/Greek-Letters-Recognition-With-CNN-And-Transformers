import cv2
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os

def exemplo_bounding_box():
    """
    Carrega uma imagem e seu respectivo PAGE XML, desenha os polígonos dos Glyphs (letras)
    e renderiza o resultado usando Matplotlib.
    
    Retorna o objeto Figure do matplotlib para controle na exibição.
    """
    BASE_PATH = "/content/drive/MyDrive/Colab Notebooks/Trabalho IA/temp/Bessarion/processing" 
    BASE_FILENAME = "145_MONI GENETHLIOY THEOTOKOY PANAGIAS VELLAS I KOKKINI EKKLISIA VOYLGARELI"
    
    image_path = os.path.join(BASE_PATH, "copias", "ruim", f"{BASE_FILENAME}.tiff")
    xml_path = os.path.join(BASE_PATH, "copias", "ruim", f"{BASE_FILENAME}.xml")

    # Verifica se os arquivos realmente existem no caminho especificado
    if not os.path.exists(image_path):
        print(f"Erro: Imagem não encontrada em {image_path}")
        return None
    if not os.path.exists(xml_path):
        print(f"Erro: XML não encontrado em {xml_path}")
        return None

    # 1. Carregar a imagem
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 2. Parse do arquivo PAGE XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Namespace padrão do PAGE XML usado no Bessarion
    ns = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}

    # 3. Buscar todas as marcações de letras (Glyph)
    glyphs = root.findall('.//ns:Glyph', ns)
    print(f"Encontradas {len(glyphs)} letras individuais (Glyphs) no XML.")

    # 4. Extrair coordenadas de cada letra e desenhar
    for glyph in glyphs:
        coords_node = glyph.find('./ns:Coords', ns)

        if coords_node is not None:
            # A string de coordenadas vem no formato "x1,y1 x2,y2 x3,y3 ..."
            points_str = coords_node.attrib.get('points', '')

            if points_str:
                # Converte a string em uma matriz NumPy de inteiros
                points = np.array([list(map(int, pt.split(','))) for pt in points_str.split()], dtype=np.int32)

                # Desenha o polígono da letra na imagem
                cv2.polylines(img_rgb, [points], isClosed=True, color=(0, 255, 255), thickness=2)

    # 5. Configurar a visualização resultante
    fig, ax = plt.subplots(figsize=(24, 24))
    ax.imshow(img_rgb)
    ax.axis('off')
    ax.set_title("Visualização das Bounding Boxes por Letra (Glyphs) - Bessarion Dataset", fontsize=16)
    
    # Exibe a imagem localmente (funciona se importado diretamente no notebook)
    plt.show()
    
    return fig
