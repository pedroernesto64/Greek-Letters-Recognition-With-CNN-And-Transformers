import os
import shutil

def separa_qualidades():
    """
    Organiza as imagens e XMLs copiados dividindo-os em subpastas de qualidade
    (ruim, ok, bom) baseando-se em mapeamentos de texto estruturados.
    """
    BASE_PATH = "/content/drive/MyDrive/Colab Notebooks/Trabalho IA"

    # Definição das pastas
    BASE_DIR = os.path.join(BASE_PATH, "temp/Bessarion/processing/copias")
    CATEGORIES = ["ruim", "ok", "bom"]

    # Listas fornecidas
    ruim_list = [
        '145_MONI GENETHLIOY THEOTOKOY PANAGIAS VELLAS I KOKKINI EKKLISIA VOYLGARELI.tiff',
        '370. KOIMISI THEOTOKOY FWTEINO 2.tiff',
        '372_KOIMISI THEOTOKOY KAPESOVO.tiff',
        '513_AG. PARASKEYI PATERO.tiff',
        '60_AG DIMITRIOS KYPSELI.jpg',
        '750_KOIMISI THEOTOKOY PLAISIA.tiff',
        '751_AG APOSTOLOI LEYKOTHEAS3.tiff',
        'DSCN3179.JPG',
        'DSCN3181.JPG',
        'DSCN3184.JPG',
        'Ktitoriki Gennesio Thotokou Koritiani.JPG'
    ]

    ok_list = [
        '1029_MONI KAMYTZIANIS AG GEWRGIOY3.tiff',
        '686_AG. GEWRGIOS KOYRENTA1.tiff',
        '242_MONI AVEL VISSANI.tiff',
        '967_AG. GEWRGIOS KATW LAPSISTA.tiff',
        '368_MONI AGIOY IWANNI LYKOTRIXI.tiff',
        'DSCN3182.JPG'
    ]

    bom_list = [
        '101_MONI STWGERIS, PANAGIAS I KOIMISIS STO ALEPOXWRI MPOTSARI2.jpg',
        '1029_MONI KAMYTZIANIS AG GEWRGIOY1.tiff',
        '1029_MONI KAMYTZIANIS AG GEWRGIOY2.tiff',
        '114_GENESIOY THEOTOKOY THESPRWTIKO.tiff',
        '20150315_144055.jpg',
        '273_MONI ELEOYSAS NISI IWANNINWN1.tiff',
        '295_ΝΑΟΣ ΑΓ. ΝΙΚΟΛΑΟΥ ΚΑΠΕΣΟΒΟ.tiff',
        '305_MONI EYAGGELISTRIAS PEDINWN2.tiff',
        '309_KOIMISI THEOTOKOY ARISTI ZAGORIOY.tiff',
        '756_AG. GEWRGIOS NEGADES1.tiff',
        '824_AG NIKOLAOS TSEPELOVO.tiff',
        '849_AG. ATHANASIOS PREVEZA.tiff',
        'Ktitoriki Elliniko.JPG',
        'n.2791 Hagios NIkolaos kalentzi.jpg'
    ]

    # Mapeamento de destino
    dataset_map = {
        "ruim": [f.strip() for f in ruim_list],
        "ok": [f.strip() for f in ok_list],
        "bom": [f.strip() for f in bom_list]
    }

    # 1. Cria as subpastas dentro de "copias"
    for cat in CATEGORIES:
        os.makedirs(os.path.join(BASE_DIR, cat), exist_ok=True)

    print("Organizando arquivos por qualidade...")

    # Contadores para o resumo
    moved_images = 0
    moved_xmls = 0

    # 2. Percorre o mapeamento e move os arquivos correspondentes
    for category, file_list in dataset_map.items():
        target_folder = os.path.join(BASE_DIR, category)

        for img_name in file_list:
            img_path = os.path.join(BASE_DIR, img_name)

            # Se a imagem existir na pasta "copias"
            if os.path.exists(img_path):
                # Move a imagem
                shutil.move(img_path, os.path.join(target_folder, img_name))
                moved_images += 1

                # Define o nome base sem a extensão para buscar os XMLs
                base_name, _ = os.path.splitext(img_name)

                # XML padrão (*.xml)
                xml1_name = f"{base_name}.xml"
                xml1_path = os.path.join(BASE_DIR, xml1_name)
                if os.path.exists(xml1_path):
                    shutil.move(xml1_path, os.path.join(target_folder, xml1_name))
                    moved_xmls += 1

                # XML temporário/secundário (*~.xml)
                xml2_name = f"{base_name}~.xml"
                xml2_path = os.path.join(BASE_DIR, xml2_name)
                if os.path.exists(xml2_path):
                    shutil.move(xml2_path, os.path.join(target_folder, xml2_name))
                    moved_xmls += 1
            else:
                print(f"Aviso: Imagem não encontrada em '{BASE_DIR}/': {img_name}")

    print("\nProcesso concluído com sucesso!")
    print(f"Imagens movidas para seus diretórios: {moved_images}")
    print(f"Arquivos XML movidos associados: {moved_xmls}")
