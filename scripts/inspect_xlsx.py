import sys
import zipfile
import xml.etree.ElementTree as ET


def col_letters(cell_ref: str) -> str:
    # "AB12" -> "AB"
    out = []
    for ch in cell_ref:
        if "A" <= ch <= "Z" or "a" <= ch <= "z":
            out.append(ch.upper())
        else:
            break
    return "".join(out)


def read_shared_strings(z: zipfile.ZipFile) -> list[str]:
    try:
        data = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(data)
    # Namespaces may be present; ignore by matching tag ending
    strings: list[str] = []
    for si in root.iter():
        if si.tag.endswith("si"):
            # A shared string can have multiple <t> nodes (rich text). Join them.
            parts: list[str] = []
            for t in si.iter():
                if t.tag.endswith("t") and t.text is not None:
                    parts.append(t.text)
            strings.append("".join(parts))
    return strings


def parse_sheet_rows(z: zipfile.ZipFile, sheet_path: str, shared: list[str]) -> list[dict[str, str]]:
    data = z.read(sheet_path)
    root = ET.fromstring(data)

    rows: list[dict[str, str]] = []
    for row in root.iter():
        if not row.tag.endswith("row"):
            continue
        row_map: dict[str, str] = {}
        for c in row:
            if not c.tag.endswith("c"):
                continue
            r = c.attrib.get("r", "")
            col = col_letters(r)
            t = c.attrib.get("t")
            v_text = ""
            v_node = None
            for child in c:
                if child.tag.endswith("v"):
                    v_node = child
                    break
            if v_node is not None and v_node.text is not None:
                v_text = v_node.text

            if t == "s":
                # shared string index
                try:
                    idx = int(v_text)
                    row_map[col] = shared[idx] if 0 <= idx < len(shared) else v_text
                except ValueError:
                    row_map[col] = v_text
            else:
                row_map[col] = v_text

        rows.append(row_map)

    return rows


def main() -> int:
    xlsx_path = sys.argv[1] if len(sys.argv) > 1 else "Допродаем вина (1).xlsx"
    try:
        with zipfile.ZipFile(xlsx_path, "r") as z:
            shared = read_shared_strings(z)
            # We assume first worksheet is sheet1.xml (common case)
            sheet_path = "xl/worksheets/sheet1.xml"
            if sheet_path not in z.namelist():
                # Fallback: find first sheet
                sheet_candidates = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
                if not sheet_candidates:
                    print("No worksheets found in xlsx.")
                    return 2
                sheet_candidates.sort()
                sheet_path = sheet_candidates[0]

            rows = parse_sheet_rows(z, sheet_path, shared)
            print("sheet_xml:", sheet_path)

            if not rows:
                print("No rows found.")
                return 3

            # headers: first row, ordered by column letters
            header_row = rows[0]
            header_cols = sorted(header_row.keys())
            headers = [header_row.get(c, "") for c in header_cols]
            print("header_cols:", header_cols)
            print("headers:", headers)

            print("sample_rows (rows 2..6):")
            for i, row in enumerate(rows[1:6], start=2):
                cols = sorted(set(header_cols) | set(row.keys()))
                values = [row.get(c, "") for c in cols]
                print(f"row {i} cols={cols} values={values}")

        return 0
    except FileNotFoundError:
        print("File not found:", xlsx_path)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

