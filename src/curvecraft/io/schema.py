"""Column schema definitions for curve data."""


REQUIRED_DIODE_COLUMNS = ("voltage_v", "current_a")
REQUIRED_MOSFET_ID_VGS_COLUMNS = ("vgs_v", "id_a")
OPTIONAL_MOSFET_ID_VGS_COLUMNS = ("vds_v",)
REQUIRED_MOSFET_ID_VDS_COLUMNS = ("vgs_v", "vds_v", "id_a")
