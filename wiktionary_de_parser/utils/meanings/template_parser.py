import wikitextparser as wtp

from wiktionary_de_parser.utils.meanings.tags import (
    CONJUNCTIONS,
    K_TEMPLATE_WHITESPACE_TRIGGERS,
    TEMPLATE_NAME_MAPPING,
)


class TemplateParser:
    def __init__(self, template: wtp.Template):
        self.template = template

    def parse_k_template(self) -> list[str] | None:
        arguments = self.template.arguments

        # Collect the positional parameters (1-7)
        positional_args: list[str] = []
        for i in range(1, 8):
            arg = next((a for a in arguments if a.name == str(i)), None)
            if arg and arg.value.strip():
                value = arg.value.strip()
                positional_args.append(TEMPLATE_NAME_MAPPING.get(value, value))

        if not positional_args:
            return None

        tags = []
        current_tag = ""

        # Iterate over the positional arguments, check for separators and
        # create tags
        for i, arg in enumerate(positional_args, 1):
            # Check for seperator value
            current_separator = next(
                (a.value for a in arguments if a.name == f"t{i}"), None
            )

            # If the separator is not defined, check if arg is in
            # K_TEMPLATE_WHITESPACE_TRIGGERS
            if not current_separator:
                if arg in K_TEMPLATE_WHITESPACE_TRIGGERS or arg in CONJUNCTIONS:
                    current_separator = "_"
                else:
                    current_separator = ","

            # If the separator is "," or ";", start a new tag
            if current_separator in (",", ";"):
                current_tag += arg
                tags.append(current_tag)
                current_tag = ""
            # If the separator is "_" add a whitespace
            elif current_separator == "_":
                current_tag += f"{arg} "
            # If the separator is ":" add a colon
            elif current_separator == ":":
                current_tag += f"{arg}: "

        # Add the last tag
        if current_tag:
            tags.append(current_tag.strip())

        return tags

    def parse_ut_template(self) -> str | None:
        return self.template.arguments[1].value

    def parse_ch_template(self) -> str | None:
        return "Schweiz und Liechtenstein"
