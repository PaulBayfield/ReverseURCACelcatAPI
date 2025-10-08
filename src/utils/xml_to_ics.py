import html
import uuid
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta


def find_first_text(elem: ET.Element, paths: list[str]) -> str | None:
    """
    Trouve le premier texte non vide dans les chemins donnés

    :param elem: Element
    :type elem: ET.Element
    :param paths: Liste de chemins à vérifier
    :type paths: list[str]
    :return: Texte trouvé ou None
    :rtype: str | None
    """
    for p in paths:
        n = elem.find(p)

        if n is not None and n.text and n.text.strip():
            return html.unescape(n.text.strip())

    return None


async def convert_xml_to_ics(xml_data: bytes) -> str:
    """
    Convertit les données XML CELCAT en format iCalendar (ICS)

    :param xml_data: Données XML CELCAT
    :type xml_data: bytes
    :return: Données iCalendar (ICS)
    :rtype: str
    """
    tree = ET.ElementTree(ET.fromstring(xml_data))
    root = tree.getroot()

    # Prepare iCalendar
    ics_lines = [
        "BEGIN:VCALENDAR",
        "PRODID:-//ReverseURCACelcatAPI//EN",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    converted = 0

    for ev in root.findall(".//event"):
        # --- Get base date (week start) and day offset ---
        date_attr = ev.get("date")
        if not date_attr:
            continue

        try:
            base_date = datetime.strptime(date_attr, "%d/%m/%Y")
        except Exception:
            continue

        # CELCAT stores <day>0</day> for Monday, 1=Tuesday, etc.
        day_tag = ev.find("day")
        day_offset = (
            int(day_tag.text) if (day_tag is not None and day_tag.text.isdigit()) else 0
        )
        event_date = base_date + timedelta(days=day_offset)

        # --- Times ---
        start_time = find_first_text(ev, ["starttime", "startTime"])
        end_time = find_first_text(ev, ["endtime", "endTime"])
        if not (start_time and end_time):
            continue

        try:
            start_dt = datetime.strptime(
                f"{event_date.strftime('%d/%m/%Y')} {start_time.strip()}",
                "%d/%m/%Y %H:%M",
            )
            end_dt = datetime.strptime(
                f"{event_date.strftime('%d/%m/%Y')} {end_time.strip()}",
                "%d/%m/%Y %H:%M",
            )
        except Exception:
            continue

        if end_dt <= start_dt:
            end_dt = start_dt + timedelta(hours=1)

        # --- Location ---
        location = find_first_text(ev, ["resources/room/item", "resources/room"])

        # --- Additional info ---
        group = find_first_text(ev, ["resources/group/item", "resources/group"])
        notes = find_first_text(ev, ["notes"])
        prettytimes = find_first_text(ev, ["prettytimes"])
        category = find_first_text(ev, ["category"])  # CM / TD / TP etc.

        module = find_first_text(ev, ["resources/module/item", "resources/module"])
        summary = f"{module} {category}"

        # --- Description (no RawWeeks) ---
        parts = []
        if group:
            parts.append(f"• {group}")
        if notes:
            parts.append(f"• {notes}")
        if prettytimes:
            parts.append(f"• {prettytimes}")
        description = "\\n".join(parts) if parts else None

        # --- UID / timestamps ---
        ev_id = ev.get("id") or str(uuid.uuid4())
        uid = f"{ev_id}-{start_dt.strftime('%Y%m%dT%H%M')}-celcat"
        dtstamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")

        # --- ICS Event ---
        ics_event = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART;TZID=Europe/Paris:{start_dt.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID=Europe/Paris:{end_dt.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{summary}",
        ]
        if location:
            ics_event.append(f"LOCATION:{location}")
        if description:
            ics_event.append(f"DESCRIPTION:{description}")
        ics_event.append("END:VEVENT")

        ics_lines.extend(ics_event)
        converted += 1

    ics_lines.append("END:VCALENDAR")

    ics_content = "\r\n".join(ics_lines)
    return ics_content
