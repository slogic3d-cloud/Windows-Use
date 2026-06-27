from enum import Enum


class Tier(str, Enum):
    GREEN = "green"    # Sofort ausführen
    YELLOW = "yellow"  # Ausführen + loggen
    RED = "red"        # Bestätigung erforderlich


TOOL_TIERS: dict[str, Tier] = {
    # GREEN — sichere UI-Aktionen
    "click_tool": Tier.GREEN,
    "type_tool": Tier.GREEN,
    "scroll_tool": Tier.GREEN,
    "move_tool": Tier.GREEN,
    "shortcut_tool": Tier.GREEN,
    "wait_tool": Tier.GREEN,
    "done_tool": Tier.GREEN,
    "app_tool": Tier.GREEN,
    "desktop_tool": Tier.GREEN,
    "multi_select_tool": Tier.GREEN,
    "multi_edit_tool": Tier.GREEN,
    # YELLOW — sensibel aber unkritisch
    "scrape_tool": Tier.YELLOW,
    "memory_tool": Tier.YELLOW,
    "file_tool": Tier.YELLOW,
    "shell_tool": Tier.YELLOW,
    "wix_orders_tool": Tier.YELLOW,
    "wix_product_tool": Tier.YELLOW,
    "gmail_read_tool": Tier.YELLOW,
    "office_create_tool": Tier.YELLOW,
    # RED — irreversibel oder geldrelevant
    "gmail_send_tool": Tier.RED,
    "office_edit_tool": Tier.RED,
}
