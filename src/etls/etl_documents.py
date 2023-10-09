from datetime import date

from src.email.send_email import send_email
from src.etls.etl_common import ETL
from src.etls.scrapper.boe import BOEScrapper
from src.initialize import initialize_app
from src.etls.defs import boe_ids

if __name__ == "__main__":
    INIT_OBJECTS = initialize_app()
    etl_job = ETL(
        config_loader=INIT_OBJECTS.config_loader, vector_store=INIT_OBJECTS.vector_store
    )
    boe_scrapper = BOEScrapper()
    docs = []
    for boe_id in boe_ids:
        url = f"https://www.boe.es/diario_boe/xml.php?id={boe_id}"
        docs.append(boe_scrapper.download_document(url))
    if docs:
        etl_job.run(docs)

    subject = "[BOE] Documents ETL executed"
    content = f"""
    Documents ETL executed
    - Documents loaded (BOE ids): {len(boe_ids)}
    - Documents loaded: {len(docs)} 
    - Database used: {INIT_OBJECTS.config_loader['vector_store']}
    """
    send_email(INIT_OBJECTS.config_loader, subject, content)
