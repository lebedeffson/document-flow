#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../ops/lib/runtime_env.sh
source "${ROOT_DIR}/../ops/lib/runtime_env.sh"
docflow_load_env "${ROOT_DIR}/.."
docflow_export_runtime

DB_CONTAINER="${RUKOVODITEL_DB_CONTAINER}"
APP_CONTAINER="${RUKOVODITEL_CONTAINER_NAME}"
DB_NAME="${RUKOVODITEL_DB_NAME}"
DB_USER="${RUKOVODITEL_DB_USER}"
DB_PASS="${RUKOVODITEL_DB_PASSWORD}"
ENTITY_ID="${ONLYOFFICE_SEED_ENTITY_ID:-25}"
ITEM_ID="${1:-${ONLYOFFICE_SEED_ITEM_ID:-1}}"
FILE_NAME="${2:-${ONLYOFFICE_SEED_FILE_NAME:-hospital-reference-document.docx}}"
DOC_LINE_1="${3:-${ONLYOFFICE_SEED_LINE_1:-Рабочий документ для совместной работы в интегрированном контуре NauDoc + Rukovoditel.}}"
DOC_LINE_2="${4:-${ONLYOFFICE_SEED_LINE_2:-Создан автоматически через seed_onlyoffice_document.sh.}}"
DOC_LINE_3="${5:-${ONLYOFFICE_SEED_LINE_3:-Документ можно безопасно использовать для пользовательского теста и демонстрации.}}"
FILE_EXTENSION="${FILE_NAME##*.}"
FILE_EXTENSION="$(printf '%s' "${FILE_EXTENSION}" | tr '[:upper:]' '[:lower:]')"

case "${FILE_EXTENSION}" in
  docx|xlsx)
    ;;
  *)
    echo "Unsupported ONLYOFFICE seed extension: ${FILE_EXTENSION}. Supported: docx, xlsx" >&2
    exit 1
    ;;
esac

sql_value() {
  docflow_docker_exec "$DB_CONTAINER" mariadb -N -s -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$1" | tr -d '\r'
}

FIELD_ID="$(sql_value "select id from app_fields where entities_id=${ENTITY_ID} and type='fieldtype_onlyoffice' order by case when name='Совместное редактирование' then 0 when name='Рабочий черновик' then 1 else 2 end, id limit 1;")"
if [[ -z "$FIELD_ID" ]]; then
  echo "ONLYOFFICE field not found for entity ${ENTITY_ID}" >&2
  exit 1
fi

FILE_ID="$(sql_value "select f.id from app_onlyoffice_files f join app_entity_${ENTITY_ID} e on e.id=${ITEM_ID} where f.field_id=${FIELD_ID} and find_in_set(f.id,e.field_${FIELD_ID}) and f.filename='${FILE_NAME}' limit 1;")"
DATE_ADDED="$(date +%s)"

if [[ -z "$FILE_ID" ]]; then
  docflow_docker_exec "$DB_CONTAINER" mariadb -N -s -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "insert into app_onlyoffice_files (entity_id, field_id, form_token, filename, sort_order, folder, filekey, download_token, date_added, created_by) values (${ENTITY_ID}, ${FIELD_ID}, '', '${FILE_NAME}', 0, '', '', '', ${DATE_ADDED}, 1); select last_insert_id();" >/tmp/onlyoffice_seed_insert.txt
  FILE_ID="$(tail -n1 /tmp/onlyoffice_seed_insert.txt | tr -d '\r')"
  rm -f /tmp/onlyoffice_seed_insert.txt
fi

TMPFILE_POSIX="$(mktemp "/tmp/onlyoffice-reference-XXXXXX.${FILE_EXTENSION}")"
TMPFILE_PY="${TMPFILE_POSIX}"
TMPFILE_DOCKER_SRC="${TMPFILE_POSIX}"

case "${OSTYPE:-}" in
  msys*|cygwin*)
    if command -v cygpath >/dev/null 2>&1; then
      TMPFILE_PY="$(cygpath -w "${TMPFILE_POSIX}")"
      TMPFILE_DOCKER_SRC="$(cygpath -w "${TMPFILE_POSIX}")"
    fi
    ;;
esac

export TMPFILE="${TMPFILE_PY}"
export DOC_LINE_1
export DOC_LINE_2
export DOC_LINE_3
export FILE_EXTENSION
python3 - <<'PY'
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

outfile = Path(os.environ['TMPFILE'])
line_1 = os.environ['DOC_LINE_1']
line_2 = os.environ['DOC_LINE_2']
line_3 = os.environ['DOC_LINE_3']
file_extension = os.environ['FILE_EXTENSION']


def xml_escape(value):
    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def build_docx():
    return {
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
    <w:p><w:r><w:t>''' + xml_escape(line_1) + '''</w:t></w:r></w:p>
    <w:p><w:r><w:t>''' + xml_escape(line_2) + '''</w:t></w:r></w:p>
    <w:p><w:r><w:t>''' + xml_escape(line_3) + '''</w:t></w:r></w:p>
    <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>
  </w:body>
</w:document>
''',
        'word/_rels/document.xml.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
''',
    }


def build_xlsx():
    metric_label = xml_escape(line_1)
    owner_label = xml_escape(line_2)
    note_label = xml_escape(line_3)
    return {
        '[Content_Types].xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>
''',
        '_rels/.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
''',
        'docProps/app.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>ONLYOFFICE seed</Application>
</Properties>
''',
        'docProps/core.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>''' + metric_label + '''</dc:title>
  <dc:creator>DocFlow</dc:creator>
</cp:coreProperties>
''',
        'xl/workbook.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <bookViews>
    <workbookView xWindow="0" yWindow="0" windowWidth="28800" windowHeight="18120"/>
  </bookViews>
  <sheets>
    <sheet name="Лист1" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
''',
        'xl/_rels/workbook.xml.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
''',
        'xl/styles.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1">
    <font>
      <sz val="11"/>
      <name val="Calibri"/>
    </font>
  </fonts>
  <fills count="2">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
  </fills>
  <borders count="1">
    <border><left/><right/><top/><bottom/><diagonal/></border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>
''',
        'xl/worksheets/sheet1.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="A1:B4"/>
  <sheetViews>
    <sheetView workbookViewId="0"/>
  </sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <sheetData>
    <row r="1">
      <c r="A1" t="inlineStr"><is><t>Показатель</t></is></c>
      <c r="B1" t="inlineStr"><is><t>Значение</t></is></c>
    </row>
    <row r="2">
      <c r="A2" t="inlineStr"><is><t>''' + metric_label + '''</t></is></c>
      <c r="B2"><v>12</v></c>
    </row>
    <row r="3">
      <c r="A3" t="inlineStr"><is><t>''' + owner_label + '''</t></is></c>
      <c r="B3"><v>3</v></c>
    </row>
    <row r="4">
      <c r="A4" t="inlineStr"><is><t>''' + note_label + '''</t></is></c>
      <c r="B4"><v>1</v></c>
    </row>
  </sheetData>
</worksheet>
''',
    }


if file_extension == 'docx':
    content = build_docx()
elif file_extension == 'xlsx':
    content = build_xlsx()
else:
    raise SystemExit(f'Unsupported file extension: {file_extension}')

with ZipFile(outfile, 'w', compression=ZIP_DEFLATED) as zf:
    for name, text in content.items():
        zf.writestr(name, text)
PY

FOLDER="${ENTITY_ID}/$(date +%Y)/$(date +%m)/$(date +%d)/${FILE_ID}"
docflow_docker_exec -u 0 "$APP_CONTAINER" sh -lc "mkdir -p /var/www/html/uploads/onlyoffice/${FOLDER}"
docflow_docker_cp_to_container "$TMPFILE_DOCKER_SRC" "$APP_CONTAINER:/var/www/html/uploads/onlyoffice/${FOLDER}/${FILE_NAME}"
docflow_docker_exec -u 0 "$APP_CONTAINER" sh -lc "chown -R www-data:www-data /var/www/html/uploads/onlyoffice/${ENTITY_ID} && chmod 755 /var/www/html/uploads/onlyoffice/${ENTITY_ID} /var/www/html/uploads/onlyoffice/${ENTITY_ID}/$(date +%Y) /var/www/html/uploads/onlyoffice/${ENTITY_ID}/$(date +%Y)/$(date +%m) /var/www/html/uploads/onlyoffice/${ENTITY_ID}/$(date +%Y)/$(date +%m)/$(date +%d) /var/www/html/uploads/onlyoffice/${FOLDER} && chmod 644 /var/www/html/uploads/onlyoffice/${FOLDER}/${FILE_NAME}"
rm -f "$TMPFILE_POSIX"

FILEKEY="${DOCFLOW_PUBLIC_HOST}-${FILE_ID}-$(date +%s)"
docflow_docker_exec "$DB_CONTAINER" mariadb -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "update app_onlyoffice_files set folder='${FOLDER}', filekey='${FILEKEY}', filename='${FILE_NAME}' where id=${FILE_ID}; update app_entity_${ENTITY_ID} set field_${FIELD_ID}='${FILE_ID}' where id=${ITEM_ID};"

echo "field_id=${FIELD_ID}"
echo "file_id=${FILE_ID}"
echo "item_id=${ITEM_ID}"
echo "folder=${FOLDER}"
echo "filename=${FILE_NAME}"
