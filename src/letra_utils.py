import os
import cv2
import shutil
import numpy as np
import xml.etree.ElementTree as ET
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import cv2
import numpy as np

def processa_letra(img_ou_caminho, points=None, target_size=64):
    """
    Recorta um caractere individual (Glyph), remove o fundo externo 
    preenchendo-o com a cor mediana interna, e redimensiona mantendo 
    a proporção usando preenchimento (padding).
    
    Retorna a imagem final processada ou None se houver falha na validação.
    """
    # Se receber uma string (caminho), faz o cv2.imread internamente
    if isinstance(img_ou_caminho, str):
        img = cv2.imread(img_ou_caminho)
        if img is None:
            print(f"Erro ao ler a imagem no caminho: {img_ou_caminho}")
            return None
    else:
        img = img_ou_caminho # Já era uma matriz

    # Geração interna dos pontos para imagens externas
    if points is None:
        h_img, w_img = img.shape[:2]
        points = np.array([
            [0, 0],
            [w_img, 0],
            [w_img, h_img],
            [0, h_img]
        ], dtype=np.int32)

    # Recorte e Validação
    x, y, w, h = cv2.boundingRect(points)
    x, y = max(0, x), max(0, y)
    roi = img[y:y+h, x:x+w].copy()

    if roi.size == 0 or w == 0 or h == 0:
        return None

    # Preenchimento de fundo (Mediana)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    mask_roi = mask[y:y+h, x:x+w]

    valid_pixels = roi[mask_roi == 255]
    if len(valid_pixels) == 0:
        return None
    median_color = np.median(valid_pixels, axis=0)

    roi[mask_roi == 0] = median_color

    # Redimensionamento (Aspect Ratio)
    aspect_ratio = w / h
    if aspect_ratio > 1:
        new_w = target_size
        new_h = int(target_size / aspect_ratio)
    else:
        new_h = target_size
        new_w = int(target_size * aspect_ratio)

    new_w, new_h = max(1, new_w), max(1, new_h)
    resized_roi = cv2.resize(roi, (new_w, new_h))

    # Padding centralizado
    pad_top = (target_size - new_h) // 2
    pad_bottom = target_size - new_h - pad_top
    pad_left = (target_size - new_w) // 2
    pad_right = target_size - new_w - pad_left

    final_img = cv2.copyMakeBorder(
        resized_roi,
        top=pad_top, bottom=pad_bottom, left=pad_left, right=pad_right,
        borderType=cv2.BORDER_CONSTANT,
        value=median_color.tolist()
    )
    
    return final_img


def extrai_letras(target_size, model):
    """
    Orquestra o processamento em lote (Batch) lendo os arquivos PAGE XML,
    extraindo caracteres através do processa_letra e salvando-os em disco.
    """
    BASE_PATH = "/content/drive/MyDrive/Colab Notebooks/Trabalho IA/"

    # Pastas de entrada e saída
    pastas_entrada = ["temp/Bessarion/processing/copias/bom", "temp/Bessarion/processing/copias/ok"]
    output_dir = os.path.join(BASE_PATH, f"data/training_data/letras_extraidas_{model}")

    # Cria a pasta de saída principal
    os.makedirs(output_dir, exist_ok=True)

    # Define o namespace
    ns = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}

    # Contadores globais
    char_counters = defaultdict(int)
    count_sucesso = 0
    arquivos_processados = 0

    for sub_pasta in pastas_entrada:
        input_dir = os.path.join(BASE_PATH, sub_pasta)

        # Pula a pasta se ela não existir
        if not os.path.exists(input_dir):
            print(f"Aviso: Pasta '{input_dir}' não encontrada. Pulando...")
            continue

        print(f"\nProcessando diretório: {sub_pasta}...")

        for file in os.listdir(input_dir):
            # Ignora arquivos que não sejam o XML principal
            if not file.endswith('.xml') or file.endswith('~.xml'):
                continue

            base_name = file.replace('.xml', '')
            image_path = os.path.join(input_dir, f"{base_name}.tiff")
            xml_path = os.path.join(input_dir, file)

            if not os.path.exists(image_path):
                continue

            img = cv2.imread(image_path)
            if img is None:
                print(f"  -> Erro ao ler imagem: {image_path}")
                continue

            tree = ET.parse(xml_path)
            root = tree.getroot()
            glyphs = root.findall('.//ns:Glyph', ns)

            for glyph in glyphs:
                # Extração de Coordenadas
                coords_node = glyph.find('./ns:Coords', ns)
                if coords_node is None: 
                    continue

                points_str = coords_node.attrib.get('points', '')
                if not points_str: 
                    continue
                points = np.array([list(map(int, pt.split(','))) for pt in points_str.split()], dtype=np.int32)

                # Extração do Texto
                text_equiv_node = glyph.find('./ns:TextEquiv/ns:Unicode', ns)
                if text_equiv_node is None or text_equiv_node.text is None: 
                    continue

                char_unicode = text_equiv_node.text.strip()
                if not char_unicode: 
                    continue
                safe_char = char_unicode.replace("/", "_").replace("\\", "_")

                # --- CHAMADA DA FUNÇÃO AUXILIAR ---
                final_img = processa_letra(img, points, target_size)
                
                if final_img is None:
                    continue

                # ==========================================
                # SALVAMENTO NAS PASTAS DE CATEGORIA
                # ==========================================
                char_counters[safe_char] += 1
                contador_formatado = f"{char_counters[safe_char]:04d}"
                filename = f"{safe_char}{contador_formatado}.png"

                # Cria a subpasta com o nome da letra
                class_dir = os.path.join(output_dir, safe_char)
                os.makedirs(class_dir, exist_ok=True)

                # Salva o arquivo na subpasta da classe correspondente
                output_path = os.path.join(class_dir, filename)
                cv2.imwrite(output_path, final_img)
                count_sucesso += 1

            arquivos_processados += 1

    # ==========================================
    # Relatório Final
    # ==========================================
    print("\n" + "="*40)
    print("EXTRAÇÃO CONCLUÍDA E ORGANIZADA POR PASTAS!")
    print("="*40)
    print(f"Arquivos XML processados: {arquivos_processados}")
    print(f"Total de caracteres extraídos: {count_sucesso}")
    print(f"Pasta de destino: {output_dir}")
    print("-" * 40)
    print("Resumo por caractere (Top 15 mais frequentes):")

    sorted_chars = sorted(char_counters.items(), key=lambda item: item[1], reverse=True)
    for char, count in sorted_chars[:15]:
        print(f"  Letra '{char}': {count} amostras")
    if len(sorted_chars) > 15:
        print(f"  ... e mais {len(sorted_chars) - 15} classes de caracteres.")

        
def plot_freq():
    """
    Coleta a quantidade de amostras por pasta de caractere, filtra classes
    com menos de 2 elementos e plota um gráfico de barras horizontal dinâmico.
    
    Retorna o objeto Figure do matplotlib.
    """
    BASE_PATH = "/content/drive/MyDrive/Colab Notebooks/Trabalho IA/data/training_data"
    dataset_dir = os.path.join(BASE_PATH, "letras_extraidas_cnn")

    # Verifica se o diretório de dados existe antes de prosseguir
    if not os.path.exists(dataset_dir):
        print(f"Erro: O diretório de letras extraídas não existe em: {dataset_dir}")
        return None

    # ==========================================
    # 2. Coleta e Filtro dos Dados
    # ==========================================
    data = []

    # Itera sobre as subpastas
    for char_folder in os.listdir(dataset_dir):
        folder_path = os.path.join(dataset_dir, char_folder)

        if os.path.isdir(folder_path):
            count = len([f for f in os.listdir(folder_path) if f.endswith('.png')])
            if count >= 2:
                data.append({'letra': char_folder, 'quantidade': count})

    # Se não houver dados que atendam ao critério, interrompe a execução
    if not data:
        print("Aviso: Nenhuma categoria possui amostras suficientes (>= 2) para plotagem.")
        return None

    # Ordena para que o maior fique no topo
    data = sorted(data, key=lambda x: x['quantidade'], reverse=False)

    # ==========================================
    # 3. Desenho do Gráfico Horizontal
    # ==========================================
    # Altura dinâmica baseada no número de categorias
    fig, ax = plt.subplots(figsize=(10, len(data) * 0.3)) 
    sns.set_theme(style="whitegrid")

    # Cria o gráfico de barras horizontais usando o eixo explicitamente
    ax.barh([d['letra'] for d in data], [d['quantidade'] for d in data], color='skyblue', edgecolor='navy')

    ax.set_title('Distribuição de Caracteres (Categorias com >= 2 elementos)', fontsize=14)
    ax.set_xlabel('Quantidade de Amostras', fontsize=12)
    ax.set_ylabel('Letra / Categoria', fontsize=12)

    # Adiciona os números exatos ao lado das barras para facilitar a leitura
    for index, value in enumerate([d['quantidade'] for d in data]):
        ax.text(value + 0.5, index, str(value), va='center', fontsize=10)

    plt.tight_layout()
    
    # Exibe no notebook se for uma chamada direta e previne renderização dupla com retorno
    plt.show()
    return fig


def filtrar_letras_raras(min_items, model):
    """
    Identifica subpastas de caracteres que possuem menos do que 'min_items' amostras
    e as move inteiras para uma pasta de rejeitadas (letras raras).
    """
    BASE_PATH = "/content/drive/MyDrive/Colab Notebooks/Trabalho IA"
    
    # Configurações de diretórios internos
    dataset_dir = os.path.join(BASE_PATH, f"data/training_data/letras_extraidas_{model}")
    rejeitadas_dir = os.path.join(BASE_PATH, "temp/letras_raras_rejeitadas")

    # Verifica se a pasta de origem existe antes de continuar
    if not os.path.exists(dataset_dir):
        print(f"Erro: O diretório de letras extraídas não existe em: {dataset_dir}")
        return

    # Cria a pasta de destino se não existir
    os.makedirs(rejeitadas_dir, exist_ok=True)

    # ==========================================
    # 2. Identificação e Movimentação
    # ==========================================
    movidas = 0

    print(f"Iniciando filtragem de categorias com menos de {min_items} elementos...")

    # Itera sobre todas as subpastas em letras_extraidas
    for char_folder in os.listdir(dataset_dir):
        folder_path = os.path.join(dataset_dir, char_folder)

        if os.path.isdir(folder_path):
            # Lista apenas os arquivos .png da categoria
            arquivos = [f for f in os.listdir(folder_path) if f.endswith('.png')]

            # Compara dinamicamente contra o argumento informado
            if len(arquivos) < min_items:
                destino_path = os.path.join(rejeitadas_dir, char_folder)

                # Move a pasta inteira para o diretório de rejeitadas
                shutil.move(folder_path, destino_path)
                print(f"  -> Movido: Categoria '{char_folder}' ({len(arquivos)} itens) para rejeitadas.")
                movidas += 1

    print(f"\nConcluído! {movidas} categorias foram movidas para 'letras_raras_rejeitadas'.")
    

def data_augmentation(target_count, model):
    """
    Identifica classes raras que possuem menos imagens que o 'target_count'
    e gera novas imagens transformadas (Data Augmentation) de forma offline 
    até que a classe atinja a meta estipulada.
    """
    BASE_PATH = "/content/drive/MyDrive/Colab Notebooks/Trabalho IA/data/training_data/"
    DATA_DIR = os.path.join(BASE_PATH, f"letras_extraidas_{model}")

    # Verifica se a pasta do dataset existe antes de iniciar
    if not os.path.exists(DATA_DIR):
        print(f"Erro: O diretório do dataset não foi encontrado em: {DATA_DIR}")
        return

    # Configurando o gerador de distorções interno
    # Usamos parâmetros controlados para simular falhas em pedras/frescos sem destruir a letra
    datagen = ImageDataGenerator(
        rotation_range=10,       # Rotação leve (±10 graus)
        width_shift_range=0.08,  # Deslocamento horizontal sutil
        height_shift_range=0.08, # Deslocamento vertical sutil
        zoom_range=0.08,         # Zoom aproximando/afastando levemente
        brightness_range=[0.8, 1.2], # Simula falhas de iluminação natural
        fill_mode='nearest'      # Preenche bordas repetindo pixels vizinhos (mantém a textura de pedra)
    )

    total_novas_imagens = 0
    classes_balanceadas = 0

    print(f"Iniciando o Data Augmentation Offline nas classes raras (Meta: {target_count} amostras)...\n")

    # Itera sobre cada subpasta de letra
    for class_name in os.listdir(DATA_DIR):
        class_path = os.path.join(DATA_DIR, class_name)

        if not os.path.isdir(class_path):
            continue

        # Lista todas as imagens originais daquela letra
        imagens = [f for f in os.listdir(class_path) if f.endswith('.png')]
        count_atual = len(imagens)

        # Filtra categorias com menos elementos que a meta (e que tenham pelo menos 1 imagem base)
        if 0 < count_atual < target_count:
            necessarias = target_count - count_atual
            print(f"Classe '{class_name}': Possui {count_atual} amostras. Gerando +{necessarias}...")

            # Carrega todas as imagens atuais para a memória para usá-las como base
            base_imgs = []
            for img_name in imagens:
                img_p = os.path.join(class_path, img_name)
                img = cv2.imread(img_p)
                if img is not None:
                    base_imgs.append(img)

            if not base_imgs: 
                continue

            # Transforma a lista de imagens num array NumPy de 4 dimensões esperado pelo Keras
            base_imgs = np.array(base_imgs)

            # Loop para gerar a quantidade exata de imagens que faltam
            count_geradas = 0
            # O flow precisa de dados no formato (batch_size, altura, largura, canais)
            for batch in datagen.flow(base_imgs, batch_size=1, save_to_dir=class_path,
                                      save_prefix=f"aug_{class_name}", save_format='png'):
                count_geradas += 1
                total_novas_imagens += 1
                if count_geradas >= necessarias:
                    break  # Para o loop assim que atingir a meta exata

            classes_balanceadas += 1

    print("\n" + "="*40)
    print("PROCESSO DE EXPANSÃO CONCLUÍDO!")
    print("="*40)
    print(f"Classes raras infladas/balanceadas: {classes_balanceadas}")
    print(f"Total de novas imagens físicas geradas: {total_novas_imagens}")
    print(f"Agora todas as categorias processadas em '{DATA_DIR}' possuem pelo menos {target_count} amostras.")
