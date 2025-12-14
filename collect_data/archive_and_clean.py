import os
import shutil
import time

# Définition des dossiers
LOGS_DIR = "logs"
LOGS_ARCHIVE = os.path.join(LOGS_DIR, "archives")
CSV_DIR = "csv"
CSV_ARCHIVE = os.path.join(CSV_DIR, "archives")
RETENTION_DAYS = 30  # Supprime les fichiers de plus de 30 jours

# Création des dossiers s'ils n'existent pas
for folder in [LOGS_DIR, LOGS_ARCHIVE, CSV_DIR, CSV_ARCHIVE]:
    os.makedirs(folder, exist_ok=True)

# Fonction pour archiver les fichiers de plus de 7 jours
def archive_old_files(source_folder, archive_folder, days=7):
    now = time.time()
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > days * 86400:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                base, ext = os.path.splitext(file_name)
                archived_name = f"{base}_{timestamp}{ext}"
                archive_path = os.path.join(archive_folder, archived_name)
                shutil.move(file_path, archive_path)
                print(f" {file_name} archivé sous {archived_name} dans {archive_folder}")

# Fonction pour supprimer les fichiers archivés de plus de 30 jours
def delete_old_archives(archive_folder):
    now = time.time()
    for file_name in os.listdir(archive_folder):
        file_path = os.path.join(archive_folder, file_name)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > RETENTION_DAYS * 86400:
                os.remove(file_path)
                print(f" {file_name} supprimé après {RETENTION_DAYS} jours")

if __name__ == "__main__":
    print(" Gestion des fichiers : Archivage et nettoyage...")
    
    # Archivage
    archive_old_files(LOGS_DIR, LOGS_ARCHIVE)
    archive_old_files(CSV_DIR, CSV_ARCHIVE)

    # Suppression des archives trop anciennes
    delete_old_archives(LOGS_ARCHIVE)
    delete_old_archives(CSV_ARCHIVE)

    print(" Processus terminé !")
