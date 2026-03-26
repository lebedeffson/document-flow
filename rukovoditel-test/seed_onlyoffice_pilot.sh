#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_CONTAINER="rukovoditel_db_test"
APP_CONTAINER="rukovoditel_test"
DB_NAME="rukovoditel"
DB_USER="rukovoditel"
DB_PASS="rukovoditel"
ENTITY_ID="25"
ITEM_ID="1"
FILE_NAME="pilot-onlyoffice.docx"

sql_value() {
  docker exec "$DB_CONTAINER" mariadb -N -s -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$1" | tr -d '\r'
}

FIELD_ID="$(sql_value "select id from app_fields where entities_id=${ENTITY_ID} and type='fieldtype_onlyoffice' order by id limit 1;")"
if [[ -z "$FIELD_ID" ]]; then
  echo "ONLYOFFICE field not found for entity ${ENTITY_ID}" >&2
  exit 1
fi

FILE_ID="$(sql_value "select f.id from app_onlyoffice_files f join app_entity_${ENTITY_ID} e on e.id=${ITEM_ID} where f.field_id=${FIELD_ID} and find_in_set(f.id,e.field_${FIELD_ID}) and f.filename='${FILE_NAME}' limit 1;")"
DATE_ADDED="$(date +%s)"

if [[ -z "$FILE_ID" ]]; then
  docker exec "$DB_CONTAINER" mariadb -N -s -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "insert into app_onlyoffice_files (entity_id, field_id, form_token, filename, sort_order, folder, filekey, download_token, date_added, created_by) values (${ENTITY_ID}, ${FIELD_ID}, '', '${FILE_NAME}', 0, '', '', '', ${DATE_ADDED}, 1); select last_insert_id();" >/tmp/onlyoffice_seed_insert.txt
  FILE_ID="$(tail -n1 /tmp/onlyoffice_seed_insert.txt | tr -d '\r')"
  rm -f /tmp/onlyoffice_seed_insert.txt
fi

TMPFILE="$(mktemp /tmp/pilot-onlyoffice-XXXXXX.docx)"
export TMPFILE
python3 - <<'PY'
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
outfile = Path(os.environ['TMPFILE'])
content = {
    '[Content_Types].xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
''',
    '_rels/.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
''',
    'word/document.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/2006/relationships" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 wp14">
  <w:body>
    <w:p><w:r><w:t>Пилотный ONLYOFFICE-документ для совместной работы в гибридном контуре NauDoc + Rukovoditel.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Создан автоматически через seed_onlyoffice_pilot.sh.</w:t></w:r></w:p>
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>
  </w:body>
</w:document>
''',
    'word/_rels/document.xml.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
''',
}
with ZipFile(outfile, 'w', compression=ZIP_DEFLATED) as zf:
    for name, text in content.items():
        zf.writestr(name, text)
PY

FOLDER="${ENTITY_ID}/$(date +%Y)/$(date +%m)/$(date +%d)/${FILE_ID}"
docker exec -u 0 "$APP_CONTAINER" sh -lc "mkdir -p /var/www/html/uploads/onlyoffice/${FOLDER}"
docker cp "$TMPFILE" "$APP_CONTAINER:/var/www/html/uploads/onlyoffice/${FOLDER}/${FILE_NAME}"
docker exec -u 0 "$APP_CONTAINER" sh -lc "chown -R www-data:www-data /var/www/html/uploads/onlyoffice/${ENTITY_ID} && chmod 755 /var/www/html/uploads/onlyoffice/${ENTITY_ID} /var/www/html/uploads/onlyoffice/${ENTITY_ID}/$(date +%Y) /var/www/html/uploads/onlyoffice/${ENTITY_ID}/$(date +%Y)/$(date +%m) /var/www/html/uploads/onlyoffice/${ENTITY_ID}/$(date +%Y)/$(date +%m)/$(date +%d) /var/www/html/uploads/onlyoffice/${FOLDER} && chmod 644 /var/www/html/uploads/onlyoffice/${FOLDER}/${FILE_NAME}"
rm -f "$TMPFILE"

FILEKEY="localhost-${FILE_ID}-$(date +%s)"
docker exec "$DB_CONTAINER" mariadb -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "update app_onlyoffice_files set folder='${FOLDER}', filekey='${FILEKEY}', filename='${FILE_NAME}' where id=${FILE_ID}; update app_entity_${ENTITY_ID} set field_${FIELD_ID}='${FILE_ID}' where id=${ITEM_ID};"

echo "field_id=${FIELD_ID}"
echo "file_id=${FILE_ID}"
echo "item_id=${ITEM_ID}"
echo "folder=${FOLDER}"
echo "filename=${FILE_NAME}"
