import os
import json
import shutil

def copia_imagens_e_xml():
    """
    Busca de forma dinâmica e copia imagens e arquivos PAGE XML associados
    com base no arquivo de recursos JSON.
    """
    BASE_PATH = "/content/drive/MyDrive/Colab Notebooks/Trabalho IA"

    # Configurações de caminhos
    JSON_FILE = os.path.join(BASE_PATH, "temp/Bessarion/dataset/nlp_resources/ktitorikes.json")
    COPIAS_DIR = os.path.join(BASE_PATH, "temp/Bessarion/processing/copias")
    FAILS_FILE = os.path.join(BASE_PATH, "temp/Bessarion/processing/fails.txt")

    # 1. Cria a pasta 'copias' se ela não existir
    os.makedirs(COPIAS_DIR, exist_ok=True)

    # 2. Inicializa/limpa o arquivo fails.txt
    with open(FAILS_FILE, "w", encoding="utf-8") as f:
        f.write("")

    # Variáveis para o resumo final
    fails_count = 0
    success_count = 0
    xml_count = 0

    print("Iniciando a busca dinâmica e cópia das imagens e arquivos XML...")

    # Verifica se o arquivo JSON existe antes de começar
    if not os.path.exists(JSON_FILE):
        print(f"Erro: O arquivo JSON não foi encontrado em: {JSON_FILE}")
        return

    # Carrega e processa o arquivo JSON
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Função auxiliar para simular o 'find' procurando o arquivo recursivamente
    def find_file(filename):
        for root, dirs, files in os.walk(BASE_PATH):
            # Ignora a própria pasta de cópias para evitar redundâncias na busca
            if COPIAS_DIR in root:
                continue
            if filename in files:
                return os.path.join(root, filename)
        return None

    # Iterar sobre a estrutura do JSON
    for site in data:
        inscriptions = site.get("inscriptions", [])
        for ins in inscriptions:
            full_string = ins.get("filename", "").strip()

            if not full_string:
                continue

            # 3. EXTRAÇÃO: Remove o padrão "{nome do autor} - "
            if " - " in full_string:
                extracted_path = full_string.split(" - ", 1)[1]
            else:
                extracted_path = full_string

            # 4. Obtém apenas o nome final do arquivo de imagem
            filename_only = os.path.basename(extracted_path)

            # 5. Busca a imagem no sistema de arquivos
            real_path = find_file(filename_only)

            if real_path:
                try:
                    # Copia a imagem
                    shutil.copy(real_path, COPIAS_DIR)
                    success_count += 1

                    # --- CÓPIA DOS ARQUIVOS XML ASSOCIADOS ---
                    base_name, _ = os.path.splitext(filename_only)

                    # Define os dois padrões possíveis de XML
                    xml_pattern1 = f"{base_name}.xml"
                    xml_pattern2 = f"{base_name}~.xml"

                    # Procura e copia o primeiro XML (*.xml)
                    real_xml_path1 = find_file(xml_pattern1)
                    if real_xml_path1:
                        shutil.copy(real_xml_path1, COPIAS_DIR)
                        xml_count += 1

                    # Procura e copia o segundo XML (*~.xml)
                    real_xml_path2 = find_file(xml_pattern2)
                    if real_xml_path2:
                        shutil.copy(real_xml_path2, COPIAS_DIR)
                        xml_count += 1

                except Exception as e:
                    fails_count += 1
                    with open(FAILS_FILE, "a", encoding="utf-8") as ff:
                        ff.write(f"FALHA NA CÓPIA: Encontrado em '{real_path}', mas erro ao copiar: {e} (Texto original: {full_string})\n")
            else:
                fails_count += 1
                with open(FAILS_FILE, "a", encoding="utf-8") as ff:
                    ff.write(f"NÃO ENCONTRADO: Procurou por '{filename_only}' (Texto original: {full_string})\n")

    print("\nProcesso concluído!")
    print(f"Imagens copiadas com sucesso: {success_count}")
    print(f"Arquivos XML copiados com sucesso: {xml_count}")
    print(f"Total de falhas registradas em {FAILS_FILE}: {fails_count}")
