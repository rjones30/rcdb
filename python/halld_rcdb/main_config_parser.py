import rcdb.config_parser
from rcdb.config_parser import ConfigFileParseResult, ConfigSection

import logging

from rcdb.log_format import BraceMessage as F


# Setup logger
log = logging.getLogger('rcdb.halld.main_config_parser')         # create run configuration standard logger


section_names = ["TRIGGER", "GLOBAL", "FCAL","BCAL","TOF","ST","TAGH", "TAGM", "PS", "PSC", "TPOL", "CDC", "FDC"]


class HallDMainConfigParseResult(object):

    def __init__(self, config_parse_result):
        assert isinstance(config_parse_result, ConfigFileParseResult)
        self.config_parse_result = config_parse_result

        self.trigger_eq = []
        self.trigger_type = []
        self.cdc_fadc125_mode = -1


def parse_file(file_name):

    parse_result = rcdb.config_parser.parse_file(file_name, section_names)

    result = HallDMainConfigParseResult(parse_result)

    # TRIGGER section
    if 'TRIGGER' in parse_result.found_section_names:
        trigger_section = parse_result.sections["TRIGGER"]
        assert isinstance(trigger_section, ConfigSection)

        # Find all TRIG_EQ lines
        result.trigger_eq = [row[1:] for row in trigger_section.rows if row[0] == 'TRIG_EQ']

        # Find all TRIG_TYPE lines
        result.trigger_type = [row[1:] for row in trigger_section.rows if row[0] == 'TRIG_TYPE']

    else:
        log.warning(F("TRIGGER section is not found in '{}'", file_name))

    # CDC section
    if 'CDC' in parse_result.found_section_names:
        cdc_section = parse_result.sections["CDC"]
        assert isinstance(cdc_section, ConfigSection)

        if 'FADC125_MODE' in cdc_section.entities:
            try:
                result.cdc_fadc125_mode = int(cdc_section.entities['FADC125_MODE'])
            except ValueError as ex:
                log.warning(F("Cant convert CDC:FADC125_MODE value '{}' to int", cdc_section.entities['FADC125_MODE']))
    else:
        log.warning(F("CDC section is not found in '{}'", file_name))







